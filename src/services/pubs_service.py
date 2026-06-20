from typing import List

from sqlalchemy.orm import Session

from dtos.pubs import PubCreateDTO, PubSearchDTO, PubUpdateDTO
from models.pub import Pub
from db.redis_client import get_redis
from configs.settings import settings
from repositories.pubs_repository import PubsRepository
from utils.amap_geocode import geocode_address


class PubsService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = PubsRepository(session)

    def sync_geo_to_redis(self) -> int:
        pubs = self.repo.list_with_coords()
        if not pubs:
            return 0
        redis = get_redis()
        geo_key = settings.redis_geo_key
        count = 0
        for pub in pubs:
            if pub.id is None:
                continue
            try:
                lon = float(pub.longitude)
                lat = float(pub.latitude)
            except (TypeError, ValueError):
                continue
            redis.geoadd(geo_key, [lon, lat, str(pub.id)])
            count += 1
        return count

    def create_pub(self, merchant_user_id: int, dto: PubCreateDTO) -> Pub:
        if not dto.address:
            raise ValueError("结构化地址不能为空")
        if dto.longitude is None or dto.latitude is None:
            lng, lat = geocode_address(dto.address, dto.city)
            dto.longitude = lng
            dto.latitude = lat
        pub = Pub(
            merchant_user_id=merchant_user_id,
            pub_name=dto.pub_name,
            cover_url=dto.cover_url,
            address=dto.address,
            longitude=dto.longitude,
            latitude=dto.latitude,
            contact_phone=dto.contact_phone,
            business_hours=dto.business_hours,
            status=dto.status,
        )
        self.repo.create(pub)
        self.session.commit()
        self._upsert_geo(pub)
        return pub

    def get_pub(self, pub_id: int) -> Pub:
        pub = self.repo.get_by_id(pub_id)
        if not pub:
            raise ValueError("酒馆不存在")
        return pub

    def update_pub(self, pub_id: int, dto: PubUpdateDTO) -> Pub:
        if dto.address and (dto.longitude is None or dto.latitude is None):
            lng, lat = geocode_address(dto.address, dto.city)
            dto.longitude = lng
            dto.latitude = lat
        fields = {k: v for k, v in dto.__dict__.items() if v is not None}
        pub = self.repo.update(pub_id, fields)
        if not pub:
            raise ValueError("酒馆不存在")
        self.session.commit()
        self._upsert_geo(pub)
        return pub

    def delete_pub(self, pub_id: int) -> None:
        pub = self.repo.get_by_id(pub_id)
        if not pub:
            raise ValueError("酒馆不存在")
        self.repo.delete(pub)
        self.session.commit()
        self._remove_geo(pub.id)

    def search_pubs(self, dto: PubSearchDTO) -> List[Pub]:
        return self.repo.search(dto.keyword, dto.offset, dto.limit)

    def search_pubs_by_beer(
        self, beer_keyword: str, in_stock_only: bool | None, offset: int, limit: int
    ):
        if not beer_keyword:
            raise ValueError("酒款关键词不能为空")
        return self.repo.search_by_beer(beer_keyword, in_stock_only, offset, limit)

    def search_pubs_by_beer_nearby(
        self,
        beer_keyword: str,
        lat: float,
        lng: float,
        radius_km: float,
        in_stock_only: bool | None,
        offset: int,
        limit: int,
    ):
        if not beer_keyword:
            raise ValueError("酒款关键词不能为空")
        redis = get_redis()
        geo_key = settings.redis_geo_key
        results = redis.geosearch(
            geo_key,
            longitude=lng,
            latitude=lat,
            radius=radius_km,
            unit="km",
            withdist=True,
            sort="ASC",
        )
        if not results:
            return []
        pub_ids = []
        distances = {}
        for member, dist in results:
            try:
                pub_id = int(member)
            except (TypeError, ValueError):
                continue
            pub_ids.append(pub_id)
            distances[pub_id] = float(dist)
        if not pub_ids:
            return []
        rows = self.repo.search_by_beer_in_pubs(beer_keyword, pub_ids, in_stock_only)
        rows.sort(key=lambda row: distances.get(row[0].id, 0))
        sliced = rows[offset : offset + limit]
        return [(pub, beer, distances.get(pub.id)) for pub, beer in sliced]

    def search_nearby_pubs(
        self,
        lat: float,
        lng: float,
        radius_km: float,
        offset: int,
        limit: int,
    ):
        """搜索半径内的所有酒馆，按距离排序"""
        redis = get_redis()
        geo_key = settings.redis_geo_key
        results = redis.geosearch(
            geo_key,
            longitude=lng,
            latitude=lat,
            radius=radius_km,
            unit="km",
            withdist=True,
            sort="ASC",
            count=offset + limit,
        )
        if not results:
            return []
        # 收集 pub_id → distance
        id_dist: dict[int, float] = {}
        for member, dist in results:
            try:
                pub_id = int(member)
            except (TypeError, ValueError):
                continue
            id_dist[pub_id] = float(dist)
        if not id_dist:
            return []
        # 按距离排序的 pub_ids
        sorted_ids = sorted(id_dist.keys(), key=lambda pid: id_dist[pid])
        sliced_ids = sorted_ids[offset : offset + limit]
        pubs = self.repo.get_pubs_by_ids(sliced_ids)
        pub_map = {p.id: p for p in pubs}
        # 保持 Redis 的排序顺序
        items = []
        for pid in sliced_ids:
            pub = pub_map.get(pid)
            if pub:
                items.append((pub, id_dist[pid]))
        return items

    def get_managed_pubs(self, role: int, user_id: int) -> list:
        """根据角色返回管理的酒馆：管理员→全部，商家→自己的，普通用户→空"""
        if role == 2:
            return self.repo.list_all_pubs()
        if role == 1:
            return self.repo.list_by_merchant(user_id)
        return []

    def _upsert_geo(self, pub: Pub) -> None:
        if pub.longitude is None or pub.latitude is None or pub.id is None:
            return
        try:
            lon = float(pub.longitude)
            lat = float(pub.latitude)
        except (TypeError, ValueError):
            return
        redis = get_redis()
        redis.geoadd(settings.redis_geo_key, [lon, lat, str(pub.id)])

    def _remove_geo(self, pub_id: int) -> None:
        redis = get_redis()
        redis.zrem(settings.redis_geo_key, str(pub_id))
