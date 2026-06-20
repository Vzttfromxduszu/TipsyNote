from dataclasses import dataclass
from typing import Optional


@dataclass
class PostCreateDTO:
    title: str
    content: str


@dataclass
class PostUpdateDTO:
    title: Optional[str] = None
    content: Optional[str] = None


@dataclass
class PostSearchDTO:
    keyword: Optional[str] = None
    user_id: Optional[int] = None
    status: Optional[int] = None
    offset: int = 0
    limit: int = 20
