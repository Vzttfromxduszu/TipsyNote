from dataclasses import dataclass
from typing import Optional


@dataclass
class PubCreateDTO:
    pub_name: str
    cover_url: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    contact_phone: Optional[str] = None
    business_hours: Optional[str] = None
    status: int = 1


@dataclass
class PubUpdateDTO:
    pub_name: Optional[str] = None
    cover_url: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    contact_phone: Optional[str] = None
    business_hours: Optional[str] = None
    status: Optional[int] = None


@dataclass
class PubSearchDTO:
    keyword: Optional[str] = None
    offset: int = 0
    limit: int = 20
