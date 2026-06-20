from typing import Optional, List

from pydantic import BaseModel


class PubCreateRequest(BaseModel):
    pub_name: str
    cover_url: Optional[str] = None
    address: str
    city: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    contact_phone: Optional[str] = None
    business_hours: Optional[str] = None
    status: int = 1


class PubUpdateRequest(BaseModel):
    pub_name: Optional[str] = None
    cover_url: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    contact_phone: Optional[str] = None
    business_hours: Optional[str] = None
    status: Optional[int] = None


class PubResponse(BaseModel):
    id: int
    merchant_user_id: int
    pub_name: str
    cover_url: Optional[str] = None
    address: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    contact_phone: Optional[str] = None
    business_hours: Optional[str] = None
    status: int


class PubListResponse(BaseModel):
    items: List[PubResponse]
    offset: int
    limit: int


class BeerPubItem(BaseModel):
    pub: PubResponse
    beer_name: str
    brewery_name: str
    style: Optional[str] = None
    price: Optional[float] = None
    status: int
    distance_km: Optional[float] = None


class BeerPubSearchResponse(BaseModel):
    items: List[BeerPubItem]
    offset: int
    limit: int


class PubNearbyItem(BaseModel):
    pub: PubResponse
    distance_km: float


class PubNearbyResponse(BaseModel):
    items: List[PubNearbyItem]
    total: int
