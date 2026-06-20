from typing import List

from sqlalchemy.orm import Session

from dtos.beer_inventory import BeerCreateDTO, BeerSearchDTO, BeerUpdateDTO
from models.beer_inventory import BeerInventory
from repositories.beer_inventory_repository import BeerInventoryRepository


class BeerInventoryService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = BeerInventoryRepository(session)

    def create_beer(self, dto: BeerCreateDTO) -> BeerInventory:
        beer = BeerInventory(
            pub_id=dto.pub_id,
            beer_name=dto.beer_name,
            brewery_name=dto.brewery_name,
            style=dto.style,
            abv=dto.abv,
            volume_ml=dto.volume_ml,
            price=dto.price,
            status=dto.status,
        )
        self.repo.create(beer)
        self.session.commit()
        return beer

    def get_beer(self, beer_id: int) -> BeerInventory:
        beer = self.repo.get_by_id(beer_id)
        if not beer:
            raise ValueError("酒款不存在")
        return beer

    def update_beer(self, beer_id: int, dto: BeerUpdateDTO) -> BeerInventory:
        fields = {k: v for k, v in dto.__dict__.items() if v is not None}
        beer = self.repo.update(beer_id, fields)
        if not beer:
            raise ValueError("酒款不存在")
        self.session.commit()
        return beer

    def delete_beer(self, beer_id: int) -> None:
        beer = self.repo.get_by_id(beer_id)
        if not beer:
            raise ValueError("酒款不存在")
        self.repo.delete(beer)
        self.session.commit()

    def search_beers(self, dto: BeerSearchDTO) -> List[BeerInventory]:
        return self.repo.search(dto.keyword, dto.pub_id, dto.status, dto.offset, dto.limit)

    def search_beers_by_style(self, style_keyword: str, offset: int, limit: int):
        if not style_keyword:
            raise ValueError("风格关键词不能为空")
        return self.repo.search_by_style_with_pub(style_keyword, offset, limit)
