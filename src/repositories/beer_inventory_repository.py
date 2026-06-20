from typing import List, Optional

from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from models.beer_inventory import BeerInventory
from models.pub import Pub


class BeerInventoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, beer_id: int) -> Optional[BeerInventory]:
        return self.session.get(BeerInventory, beer_id)

    def create(self, beer: BeerInventory) -> BeerInventory:
        self.session.add(beer)
        self.session.flush()
        return beer

    def update(self, beer_id: int, fields: dict) -> Optional[BeerInventory]:
        if not fields:
            return self.get_by_id(beer_id)
        stmt = update(BeerInventory).where(BeerInventory.id == beer_id).values(**fields)
        self.session.execute(stmt)
        return self.get_by_id(beer_id)

    def delete(self, beer: BeerInventory) -> None:
        self.session.delete(beer)

    def search(
        self,
        keyword: Optional[str],
        pub_id: Optional[int],
        status: Optional[int],
        offset: int,
        limit: int,
    ) -> List[BeerInventory]:
        stmt = select(BeerInventory)
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(
                or_(
                    BeerInventory.beer_name.like(like),
                    BeerInventory.brewery_name.like(like),
                    BeerInventory.style.like(like),
                )
            )
        if pub_id is not None:
            stmt = stmt.where(BeerInventory.pub_id == pub_id)
        if status is not None:
            stmt = stmt.where(BeerInventory.status == status)
        stmt = stmt.offset(offset).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def search_by_style_with_pub(
        self,
        style_keyword: str,
        offset: int,
        limit: int,
    ):
        keyword = style_keyword.strip()
        if not keyword:
            return []
        like = f"%{keyword}%"
        stmt = (
            select(BeerInventory, Pub)
            .join(Pub, Pub.id == BeerInventory.pub_id)
            .where(BeerInventory.style.like(like))
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.execute(stmt).all())
