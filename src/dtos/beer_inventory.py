from dataclasses import dataclass
from typing import Optional


@dataclass
class BeerCreateDTO:
    pub_id: int
    beer_name: str
    brewery_name: str
    style: Optional[str] = None
    abv: Optional[float] = None
    volume_ml: Optional[int] = None
    price: Optional[float] = None
    status: int = 1


@dataclass
class BeerUpdateDTO:
    beer_name: Optional[str] = None
    brewery_name: Optional[str] = None
    style: Optional[str] = None
    abv: Optional[float] = None
    volume_ml: Optional[int] = None
    price: Optional[float] = None
    status: Optional[int] = None


@dataclass
class BeerSearchDTO:
    keyword: Optional[str] = None
    pub_id: Optional[int] = None
    status: Optional[int] = None
    offset: int = 0
    limit: int = 20
