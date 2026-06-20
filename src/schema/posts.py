from typing import List, Optional

from pydantic import BaseModel


class PostResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    like_count: int
    comment_count: int
    status: int
    created_at: str
    updated_at: str
    user_nickname: Optional[str] = None
    user_avatar: Optional[str] = None
    liked: bool = False


class PostListResponse(BaseModel):
    items: List[PostResponse]
    offset: int
    limit: int


class PostCreateRequest(BaseModel):
    title: str
    content: str


class PostUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None
