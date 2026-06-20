from typing import Optional
from pathlib import Path as PathLib
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from configs.settings import settings
from dtos.pubs import PubCreateDTO, PubSearchDTO, PubUpdateDTO
from schema.pubs import (
    PubCreateRequest,
    PubUpdateRequest,
    PubResponse,
    PubListResponse,
    BeerPubSearchResponse,
    PubNearbyResponse,
)
from services.pubs_service import PubsService
from utils.amap_walking import get_walking_route
from utils.amap_driving import get_driving_route
from utils.geo_distance import haversine_km


router = APIRouter(tags=["pubs"])


def _to_pub_response(pub) -> dict:
    return {
        "id": pub.id,
        "merchant_user_id": pub.merchant_user_id,
        "pub_name": pub.pub_name,
        "cover_url": pub.cover_url,
        "address": pub.address,
        "longitude": float(pub.longitude) if pub.longitude is not None else None,
        "latitude": float(pub.latitude) if pub.latitude is not None else None,
        "contact_phone": pub.contact_phone,
        "business_hours": pub.business_hours,
        "status": pub.status,
    }


@router.post("/pubs", response_model=PubResponse)
def create_pub(
    payload: PubCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role not in (1, 2):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅商家可创建酒馆")
    service = PubsService(db)
    try:
        pub = service.create_pub(current_user.id, PubCreateDTO(**payload.model_dump()))
        return _to_pub_response(pub)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/pubs/by-beer", response_model=BeerPubSearchResponse)
def search_pubs_by_beer(
    beer_name: str,
    in_stock_only: Optional[bool] = None,
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    service = PubsService(db)
    rows = service.search_pubs_by_beer(beer_name, in_stock_only, offset, limit)
    items = []
    for pub, beer in rows:
        items.append(
            {
                "pub": _to_pub_response(pub),
                "beer_name": beer.beer_name,
                "brewery_name": beer.brewery_name,
                "style": beer.style,
                "price": float(beer.price) if beer.price is not None else None,
                "status": beer.status,
            }
        )
    return {"items": items, "offset": offset, "limit": limit}

# 该接口会根据用户提供的经纬度和搜索半径，返回附近提供特定酒款的酒馆列表，帮助用户快速找到想喝的酒款在哪些酒馆有售，并且这些酒馆距离用户的位置有多远。
@router.get("/pubs/by-beer-nearby", response_model=BeerPubSearchResponse)
def search_pubs_by_beer_nearby(
    beer_name: str,
    lat: float,
    lng: float,
    radius_km: float = 10.0,
    in_stock_only: Optional[bool] = None,
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    service = PubsService(db)
    rows = service.search_pubs_by_beer_nearby(
        beer_name, lat, lng, radius_km, in_stock_only, offset, limit
    )
    items = []
    for pub, beer, distance_km in rows:
        items.append(
            {
                "pub": _to_pub_response(pub),
                "beer_name": beer.beer_name,
                "brewery_name": beer.brewery_name,
                "style": beer.style,
                "price": float(beer.price) if beer.price is not None else None,
                "status": beer.status,
                "distance_km": distance_km,
            }
        )
    return {"items": items, "offset": offset, "limit": limit}


@router.get("/pubs/nearby", response_model=PubNearbyResponse)
def search_nearby_pubs(
    lat: float,
    lng: float,
    radius_km: float = 20.0,
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """搜索附近一定范围内的所有酒馆，按距离由近到远排序"""
    service = PubsService(db)
    rows = service.search_nearby_pubs(lat, lng, radius_km, offset, limit)
    items = []
    for pub, dist in rows:
        items.append({"pub": _to_pub_response(pub), "distance_km": round(dist, 2)})
    return {"items": items, "total": len(rows)}


@router.get("/pubs/{pub_id}", response_model=PubResponse)
def get_pub(pub_id: int, db: Session = Depends(get_db)):
    service = PubsService(db)
    pub = service.get_pub(pub_id)
    return _to_pub_response(pub)


@router.get("/pubs/{pub_id}/walking")
def get_pub_walking_route(
    pub_id: int,
    origin_lng: float,
    origin_lat: float,
    db: Session = Depends(get_db),
):
    service = PubsService(db)
    pub = service.get_pub(pub_id)
    if pub.longitude is None or pub.latitude is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="酒馆缺少坐标")
    try:
        distance_m, duration_min = get_walking_route(
            origin_lng, origin_lat, float(pub.longitude), float(pub.latitude)
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {
        "distance_m": distance_m,
        "duration_min": duration_min,
        "origin": {"lng": origin_lng, "lat": origin_lat},
        "destination": {"lng": float(pub.longitude), "lat": float(pub.latitude)},
    }

# 路径规划接口：根据用户提供的起点坐标和酒馆ID，返回从起点到酒馆的路径信息，包括距离和预计时间。对于较近的距离（如2公里以内），提供步行路径；对于较远的距离，提供驾车路径。
@router.get("/pubs/{pub_id}/route")
def get_pub_route(
    pub_id: int,
    origin_lng: float,
    origin_lat: float,
    db: Session = Depends(get_db),
):
    service = PubsService(db)
    pub = service.get_pub(pub_id)
    if pub.longitude is None or pub.latitude is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="酒馆缺少坐标")
    dest_lng = float(pub.longitude)
    dest_lat = float(pub.latitude)
    try:
        distance_km = haversine_km(origin_lng, origin_lat, dest_lng, dest_lat)
        if distance_km <= 2:
            distance_m, duration_min = get_walking_route(origin_lng, origin_lat, dest_lng, dest_lat)
            mode = "walking"
        else:
            distance_m, duration_min = get_driving_route(origin_lng, origin_lat, dest_lng, dest_lat)
            mode = "driving"
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {
        "mode": mode,
        "distance_m": distance_m,
        "duration_min": duration_min,
        "origin": {"lng": origin_lng, "lat": origin_lat},
        "destination": {"lng": dest_lng, "lat": dest_lat},
    }


@router.put("/pubs/{pub_id}", response_model=PubResponse)
def update_pub(
    pub_id: int,
    payload: PubUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PubsService(db)
    pub = service.get_pub(pub_id)
    if current_user.role != 2 and pub.merchant_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限修改该酒馆")
    try:
        pub = service.update_pub(pub_id, PubUpdateDTO(**payload.model_dump()))
        return _to_pub_response(pub)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/pubs/{pub_id}/cover")
def upload_pub_cover(
    pub_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """上传酒馆封面图片（仅商家本人或管理员）"""
    service = PubsService(db)
    pub = service.get_pub(pub_id)
    if current_user.role != 2 and pub.merchant_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限修改该酒馆")
    ext = PathLib(file.filename or "").suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 JPG/PNG")
    content = file.file.read()
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="图片需小于 2MB")
    covers_dir = PathLib(settings.storage_path) / "covers"
    covers_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = covers_dir / filename
    with filepath.open("wb") as f:
        f.write(content)
    cover_url = f"/api/covers/{filename}"
    pub = service.update_pub(pub_id, PubUpdateDTO(cover_url=cover_url))
    return {"cover_url": cover_url}


# 该接口会根据用户提供的酒馆ID，删除对应的酒馆信息，帮助商家管理自己的酒馆列表。需要注意的是，只有酒馆所属的商家才能删除该酒馆，其他用户无权限操作。
@router.delete("/pubs/{pub_id}")
def delete_pub(
    pub_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PubsService(db)
    pub = service.get_pub(pub_id)
    if current_user.role != 2 and pub.merchant_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限删除该酒馆")
    service.delete_pub(pub_id)
    return {"deleted": True}

# 该接口会根据用户提供的关键词，返回包含该关键词的酒馆列表，帮助用户快速找到想去的酒馆。
@router.get("/pubs", response_model=PubListResponse)
def search_pubs(
    keyword: Optional[str] = None,
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    service = PubsService(db)
    dto = PubSearchDTO(keyword=keyword, offset=offset, limit=limit)
    pubs = service.search_pubs(dto)
    return {
        "items": [_to_pub_response(p) for p in pubs],
        "offset": offset,
        "limit": limit,
    }

