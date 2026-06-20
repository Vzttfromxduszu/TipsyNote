from typing import List, Optional

from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from models.post import Post
from models.post_like import PostLike


class PostsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, post_id: int) -> Optional[Post]:
        return self.session.get(Post, post_id)

    def create(self, post: Post) -> Post:
        self.session.add(post)
        self.session.flush()
        return post

    def update(self, post_id: int, fields: dict) -> Optional[Post]:
        if not fields:
            return self.get_by_id(post_id)
        stmt = update(Post).where(Post.id == post_id).values(**fields)
        self.session.execute(stmt)
        return self.get_by_id(post_id)

    def delete(self, post: Post) -> None:
        self.session.delete(post)

    def search(
        self,
        keyword: Optional[str],
        user_id: Optional[int],
        status: Optional[int],
        offset: int,
        limit: int,
    ) -> List[Post]:
        stmt = select(Post)
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(or_(Post.title.like(like), Post.content.like(like)))
        if user_id is not None:
            stmt = stmt.where(Post.user_id == user_id)
        if status is not None:
            stmt = stmt.where(Post.status == status)
        stmt = stmt.order_by(Post.created_at.desc()).offset(offset).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def find_liked_by_user(
        self,
        user_id: int,
        offset: int,
        limit: int,
    ) -> List[Post]:
        stmt = (
            select(Post)
            .join(PostLike, PostLike.post_id == Post.id)
            .where(PostLike.user_id == user_id)
            .order_by(PostLike.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())
