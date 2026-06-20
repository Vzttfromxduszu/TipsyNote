from typing import Optional, List

from pydantic import BaseModel, Field

from schema.schemas_auth import LoginRequest, TokenResponse, CurrentUserResponse


class SendCodeRequest(BaseModel):
    phone: str


class UserCreateRequest(BaseModel):
    phone: str
    secret: str = Field(min_length=6)
    code: str = Field(min_length=6, max_length=6)
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None


class UserUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    secret: Optional[str] = Field(default=None, min_length=6)
    status: Optional[int] = None


class UserSearchResponseItem(BaseModel):
    id: int
    phone: str
    nickname: Optional[str] = None
    role: int


class UserCreateResponse(BaseModel):
    id: int
    phone: str
    nickname: Optional[str] = None


class UserSearchResponse(BaseModel):
    items: List[UserSearchResponseItem]
    offset: int
    limit: int