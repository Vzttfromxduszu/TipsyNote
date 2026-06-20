from typing import List

from pydantic import BaseModel, Field

from schema.pubs import PubResponse


class LoginRequest(BaseModel):
    phone: str
    secret: str = Field(min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class CurrentUserResponse(BaseModel):
    id: int
    phone: str
    nickname: str | None = None
    avatar_url: str | None = None
    role: int
    status: int
    managed_pubs: List[PubResponse] = []