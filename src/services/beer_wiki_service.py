from typing import List, Tuple, Optional

from sqlalchemy.orm import Session

from dtos.beer_wiki import BeerWikiSearchDTO
from models.beer_style import BeerStyle
from models.beer_item import BeerItem
from repositories.beer_wiki_repository import BeerWikiRepository


class BeerWikiService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = BeerWikiRepository(session)

    # ── 品类 ──
    def get_all_styles(self) -> List[BeerStyle]:
        return self.repo.get_all_styles()

    def get_style_detail(self, style_id: int) -> BeerStyle:
        style = self.repo.get_style_by_id(style_id)
        if not style:
            raise ValueError("风格品类不存在")
        return style

    # ── 酒款 ──
    def get_item_detail(self, item_id: int) -> BeerItem:
        item = self.repo.get_item_by_id(item_id)
        if not item:
            raise ValueError("酒款不存在")
        return item

    def get_items_by_style(self, style_id: int) -> List[BeerItem]:
        return self.repo.get_items_by_style(style_id)

    def get_classics_by_style(self, style_id: int) -> List[BeerItem]:
        return self.repo.get_classic_items_by_style(style_id)

    # ── 搜索 & 联想 ──
    def search(self, dto: BeerWikiSearchDTO) -> Tuple[List[BeerStyle], List[BeerItem]]:
        """搜索：同时匹配品类和酒款"""
        styles = self.repo.search_styles(dto.q, dto.limit)
        items = self.repo.search_items(dto.q, dto.limit)
        return styles, items

    def get_all_classics(self) -> List[BeerItem]:
        return self.repo.get_all_classic_items()

    def suggest(self, q: str, limit: int = 8) -> List[dict]:
        """搜索联想：返回 {type, id, name, subtitle} 列表"""
        results: List[dict] = []
        styles = self.repo.search_styles(q, limit // 2)
        for s in styles:
            results.append({
                "type": "style",
                "id": s.id,
                "name": s.name,
                "subtitle": s.name_en or s.category,
            })
        items = self.repo.search_items_by_name(q, limit - len(results))
        for i in items:
            results.append({
                "type": "beer",
                "id": i.id,
                "name": i.name,
                "subtitle": f"{i.brewery or ''} · {i.country or ''}".strip(" ·"),
            })
        return results[:limit]
