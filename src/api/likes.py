"""点赞 API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from models.post_like import PostLike
from models.post import Post

router = APIRouter(tags=["likes"])


@router.post("/posts/{post_id}/likes/toggle")
def toggle_like(
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")

    existing = (
        db.query(PostLike)
        .filter(PostLike.post_id == post_id, PostLike.user_id == current_user.id)
        .first()
    )

    if existing:
        db.delete(existing)
        post.like_count = max(0, (post.like_count or 0) - 1)
        db.commit()
        return {"liked": False, "like_count": post.like_count}
    else:
        like = PostLike(post_id=post_id, user_id=current_user.id)
        db.add(like)
        post.like_count = (post.like_count or 0) + 1
        db.commit()
        return {"liked": True, "like_count": post.like_count}


@router.get("/posts/{post_id}/likes/status")
def get_like_status(
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existing = (
        db.query(PostLike)
        .filter(PostLike.post_id == post_id, PostLike.user_id == current_user.id)
        .first()
    )
    return {"liked": existing is not None}
