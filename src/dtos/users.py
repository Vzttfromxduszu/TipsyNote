from dataclasses import dataclass
from typing import Optional


@dataclass
class UserCreateDTO:
    phone: str
    secret: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    role: int = 0


@dataclass
class UserUpdateDTO:
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    secret: Optional[str] = None
    status: Optional[int] = None


@dataclass
class UserSearchDTO:
    keyword: Optional[str] = None
    role: Optional[int] = None
    status: Optional[int] = None
    offset: int = 0
    limit: int = 20
