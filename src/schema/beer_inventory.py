from typing import Optional, List

from pydantic import BaseModel


class BeerCreateRequest(BaseModel):
    pub_id: int
    beer_name: str
    brewery_name: str
    style: Optional[str] = None
    abv: Optional[float] = None
    volume_ml: Optional[int] = None
    price: Optional[float] = None
    status: int = 1


class BeerUpdateRequest(BaseModel):
    beer_name: Optional[str] = None
    brewery_name: Optional[str] = None
    style: Optional[str] = None
    abv: Optional[float] = None
    volume_ml: Optional[int] = None
    price: Optional[float] = None
    status: Optional[int] = None


class BeerResponse(BaseModel):
    id: int
    pub_id: int
    beer_name: str
    brewery_name: str
    style: Optional[str] = None
    abv: Optional[float] = None
    volume_ml: Optional[int] = None
    price: Optional[float] = None
    status: int


class BeerListResponse(BaseModel):
    items: List[BeerResponse]
    offset: int
    limit: int


class BeerWithPubItem(BaseModel):
    beer: BeerResponse
    pub: dict


class BeerStyleSearchResponse(BaseModel):
    items: List[BeerWithPubItem]
    offset: int
    limit: int
