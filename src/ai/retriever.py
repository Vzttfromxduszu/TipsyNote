from typing import List

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from models.beer_inventory import BeerInventory


def retrieve_beer_context(
    session: Session,
    mood: str,
    tastes: List[str],
    scene: str,
    style: str,
    limit: int = 10,
) -> List[str]:
    keyword_list = [style] + tastes
    conditions = []
    for kw in keyword_list:
        if kw:
            like = f"%{kw}%"
            conditions.append(
                or_(
                    BeerInventory.beer_name.like(like),
                    BeerInventory.brewery_name.like(like),
                    BeerInventory.style.like(like),
                )
            )
    stmt = select(BeerInventory)
    if conditions:
        stmt = stmt.where(or_(*conditions))
    stmt = stmt.limit(limit)
    rows = session.execute(stmt).scalars().all()
    return [
        f"{row.beer_name}｜{row.brewery_name}｜{row.style or '-'}"
        for row in rows
    ]