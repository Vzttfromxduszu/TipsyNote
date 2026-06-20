from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user, get_optional_user
from dtos.posts import PostCreateDTO, PostSearchDTO, PostUpdateDTO
from schema.posts import PostCreateRequest, PostUpdateRequest, PostResponse, PostListResponse
from services.posts_service import PostsService
from models.post_like import PostLike
from models.user import User
from utils.avatar_url import normalize_avatar_url


router = APIRouter(tags=["posts"])


def _to_post_response(post, db: Session, current_user_id: Optional[int] = None) -> dict:
    user = db.get(User, post.user_id)
    liked = False
    if current_user_id:
        liked = db.query(PostLike).filter(
            PostLike.post_id == post.id, PostLike.user_id == current_user_id
        ).first() is not None
    return {
        "id": post.id,
        "user_id": post.user_id,
        "title": post.title,
        "content": post.content,
        "like_count": post.like_count or 0,
        "comment_count": post.comment_count or 0,
        "status": post.status,
        "created_at": post.created_at.isoformat() if isinstance(post.created_at, datetime) else str(post.created_at),
        "updated_at": post.updated_at.isoformat() if isinstance(post.updated_at, datetime) else str(post.updated_at),
        "user_nickname": user.nickname if user else None,
        "user_avatar": normalize_avatar_url(user.avatar_url) if user else None,
        "liked": liked,
    }


@router.post("/posts", response_model=PostResponse)
def create_post(
    payload: PostCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PostsService(db)
    post = service.create_post(current_user.id, PostCreateDTO(**payload.model_dump()))
    db.refresh(post)
    return _to_post_response(post, db, current_user.id)


@router.get("/posts/liked", response_model=PostListResponse)
def get_liked_posts(
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PostsService(db)
    posts = service.get_liked_posts(current_user.id, offset, limit)
    return {
        "items": [_to_post_response(p, db, current_user.id) for p in posts],
        "offset": offset,
        "limit": limit,
    }


@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_user),
):
    service = PostsService(db)
    try:
        post = service.get_post(post_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return _to_post_response(post, db, current_user.id if current_user else None)


@router.put("/posts/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    payload: PostUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PostsService(db)
    post = service.get_post(post_id)
    if post.user_id != current_user.id and current_user.role != 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限修改该帖子")
    try:
        post = service.update_post(post_id, PostUpdateDTO(**payload.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return _to_post_response(post, db, current_user.id)


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PostsService(db)
    post = service.get_post(post_id)
    if post.user_id != current_user.id and current_user.role != 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限删除该帖子")
    try:
        service.delete_post(post_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return {"deleted": True}


@router.get("/posts", response_model=PostListResponse)
def search_posts(
    keyword: Optional[str] = None,
    user_id: Optional[int] = None,
    status: Optional[int] = None,
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_user),
):
    service = PostsService(db)
    dto = PostSearchDTO(keyword=keyword, user_id=user_id, status=status, offset=offset, limit=limit)
    posts = service.search_posts(dto)
    current_uid = current_user.id if current_user else None
    return {
        "items": [_to_post_response(p, db, current_uid) for p in posts],
        "offset": offset,
        "limit": limit,
    }
