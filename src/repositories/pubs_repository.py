from typing import List, Optional, Tuple

from sqlalchemy import select, update, and_, or_
from sqlalchemy.orm import Session

from models.beer_inventory import BeerInventory
from models.pub import Pub


class PubsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, pub_id: int) -> Optional[Pub]:
        return self.session.get(Pub, pub_id)

    def create(self, pub: Pub) -> Pub:
        self.session.add(pub)
        self.session.flush()
        return pub

    def update(self, pub_id: int, fields: dict) -> Optional[Pub]:
        if not fields:
            return self.get_by_id(pub_id)
        stmt = update(Pub).where(Pub.id == pub_id).values(**fields)
        self.session.execute(stmt)
        return self.get_by_id(pub_id)

    def delete(self, pub: Pub) -> None:
        self.session.delete(pub)

    def search(self, keyword: Optional[str], offset: int, limit: int) -> List[Pub]:
        stmt = select(Pub)
        if keyword:
            stmt = stmt.where(Pub.pub_name.like(f"%{keyword}%"))
        stmt = stmt.offset(offset).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def list_with_coords(self) -> List[Pub]:
        stmt = select(Pub).where(Pub.longitude.is_not(None), Pub.latitude.is_not(None))
        return list(self.session.execute(stmt).scalars().all())

    def list_by_merchant(self, merchant_user_id: int) -> List[Pub]:
        stmt = select(Pub).where(Pub.merchant_user_id == merchant_user_id)
        return list(self.session.execute(stmt).scalars().all())

    def list_all_pubs(self) -> List[Pub]:
        stmt = select(Pub)
        return list(self.session.execute(stmt).scalars().all())

    def search_by_beer(
        self,
        beer_keyword: str,
        in_stock_only: Optional[bool],
        offset: int,
        limit: int,
    ) -> List[Tuple[Pub, BeerInventory]]:
        keyword = beer_keyword.strip()
        if not keyword:
            return []
        like = f"%{keyword}%"
        stmt = (
            select(Pub, BeerInventory)
            .join(BeerInventory, BeerInventory.pub_id == Pub.id)
            .where(
                and_(
                    or_(
                        BeerInventory.beer_name.like(like),
                        BeerInventory.brewery_name.like(like),
                        BeerInventory.style.like(like),
                    ),
                )
            )
        )
        if in_stock_only is True:
            stmt = stmt.where(BeerInventory.status == 1)
        stmt = stmt.offset(offset).limit(limit)
        return list(self.session.execute(stmt).all())

    def get_pubs_by_ids(self, pub_ids: List[int]) -> List[Pub]:
        """根据 ID 列表批量查询酒馆"""
        if not pub_ids:
            return []
        stmt = select(Pub).where(Pub.id.in_(pub_ids))
        return list(self.session.execute(stmt).scalars().all())

    def search_by_beer_in_pubs(
        self,
        beer_keyword: str,
        pub_ids: List[int],
        in_stock_only: Optional[bool],
    ) -> List[Tuple[Pub, BeerInventory]]:
        if not pub_ids:
            return []
        keyword = beer_keyword.strip()
        if not keyword:
            return []
        like = f"%{keyword}%"
        stmt = (
            select(Pub, BeerInventory)
            .join(BeerInventory, BeerInventory.pub_id == Pub.id)
            .where(
                and_(
                    or_(
                        BeerInventory.beer_name.like(like),
                        BeerInventory.brewery_name.like(like),
                        BeerInventory.style.like(like),
                    ),
                    Pub.id.in_(pub_ids),
                )
            )
        )
        if in_stock_only is True:
            stmt = stmt.where(BeerInventory.status == 1)
        return list(self.session.execute(stmt).all())
