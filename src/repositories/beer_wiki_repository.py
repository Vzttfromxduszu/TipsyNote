from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from models.beer_style import BeerStyle
from models.beer_item import BeerItem


class BeerWikiRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # ── 风格品类 ──
    def get_all_styles(self) -> List[BeerStyle]:
        stmt = select(BeerStyle).order_by(BeerStyle.sort_order, BeerStyle.id)
        return list(self.session.execute(stmt).scalars().all())

    def get_style_by_id(self, style_id: int) -> Optional[BeerStyle]:
        return self.session.get(BeerStyle, style_id)

    def search_styles(self, q: str, limit: int = 10) -> List[BeerStyle]:
        like = f"%{q}%"
        stmt = (
            select(BeerStyle)
            .where(
                or_(
                    BeerStyle.name.like(like),
                    BeerStyle.name_en.like(like),
                    BeerStyle.description.like(like),
                )
            )
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())

    # ── 酒款 ──
    def get_item_by_id(self, item_id: int) -> Optional[BeerItem]:
        return self.session.get(BeerItem, item_id)

    def get_items_by_style(self, style_id: int) -> List[BeerItem]:
        stmt = (
            select(BeerItem)
            .where(BeerItem.style_id == style_id)
            .order_by(BeerItem.is_classic.desc(), BeerItem.name)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_classic_items_by_style(self, style_id: int) -> List[BeerItem]:
        stmt = (
            select(BeerItem)
            .where(BeerItem.style_id == style_id, BeerItem.is_classic == 1)
            .order_by(BeerItem.name)
        )
        return list(self.session.execute(stmt).scalars().all())

    def search_items(self, q: str, limit: int = 10) -> List[BeerItem]:
        like = f"%{q}%"
        stmt = (
            select(BeerItem)
            .where(
                or_(
                    BeerItem.name.like(like),
                    BeerItem.name_en.like(like),
                    BeerItem.brewery.like(like),
                    BeerItem.description.like(like),
                    BeerItem.flavor_tags.like(like),
                )
            )
            .order_by(BeerItem.is_classic.desc(), BeerItem.name)
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_all_classic_items(self) -> List[BeerItem]:
        stmt = (
            select(BeerItem)
            .where(BeerItem.is_classic == 1)
            .order_by(BeerItem.name)
        )
        return list(self.session.execute(stmt).scalars().all())

    def search_items_by_name(self, q: str, limit: int = 5) -> List[BeerItem]:
        """只按酒名搜索，用于联想"""
        like = f"%{q}%"
        stmt = (
            select(BeerItem)
            .where(
                or_(
                    BeerItem.name.like(like),
                    BeerItem.name_en.like(like),
                )
            )
            .order_by(BeerItem.is_classic.desc())
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())
