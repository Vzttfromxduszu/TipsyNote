"""评论 API"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from api.deps import get_db, get_current_user
from models.post_comment import PostComment
from models.post import Post
from models.user import User
from utils.avatar_url import normalize_avatar_url

router = APIRouter(tags=["comments"])


class CommentCreateRequest(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    created_at: str
    user_nickname: Optional[str] = None
    user_avatar: Optional[str] = None


class CommentListResponse(BaseModel):
    items: List[CommentResponse]


def _to_comment_response(comment: PostComment, db: Session) -> dict:
    user = db.get(User, comment.user_id)
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "user_id": comment.user_id,
        "content": comment.content,
        "created_at": comment.created_at.isoformat() if isinstance(comment.created_at, datetime) else str(comment.created_at),
        "user_nickname": user.nickname if user else None,
        "user_avatar": normalize_avatar_url(user.avatar_url) if user else None,
    }


@router.post("/posts/{post_id}/comments", response_model=CommentResponse)
def create_comment(
    post_id: int,
    payload: CommentCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")
    comment = PostComment(
        post_id=post_id,
        user_id=current_user.id,
        content=payload.content,
    )
    db.add(comment)
    # 更新帖子评论计数
    post.comment_count = (post.comment_count or 0) + 1
    db.commit()
    db.refresh(comment)
    return _to_comment_response(comment, db)


@router.get("/posts/{post_id}/comments", response_model=CommentListResponse)
def list_comments(
    post_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")
    stmt = (
        db.query(PostComment)
        .filter(PostComment.post_id == post_id)
        .order_by(PostComment.created_at.asc())
        .offset(offset)
        .limit(limit)
    )
    comments = stmt.all()
    return {"items": [_to_comment_response(c, db) for c in comments]}
