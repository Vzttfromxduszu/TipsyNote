from typing import List

from sqlalchemy.orm import Session

from dtos.posts import PostCreateDTO, PostSearchDTO, PostUpdateDTO
from models.post import Post
from repositories.posts_repository import PostsRepository


class PostsService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = PostsRepository(session)

    def create_post(self, user_id: int, dto: PostCreateDTO) -> Post:
        post = Post(
            user_id=user_id,
            title=dto.title,
            content=dto.content,
            status=1,
        )
        self.repo.create(post)
        self.session.commit()
        return post

    def get_post(self, post_id: int) -> Post:
        post = self.repo.get_by_id(post_id)
        if not post:
            raise ValueError("帖子不存在")
        return post

    def update_post(self, post_id: int, dto: PostUpdateDTO) -> Post:
        post = self.repo.get_by_id(post_id)
        if not post:
            raise ValueError("帖子不存在")
        fields = {k: v for k, v in dto.__dict__.items() if v is not None}
        post = self.repo.update(post_id, fields)
        self.session.commit()
        return post

    def delete_post(self, post_id: int) -> None:
        post = self.repo.get_by_id(post_id)
        if not post:
            raise ValueError("帖子不存在")
        self.repo.delete(post)
        self.session.commit()

    def search_posts(self, dto: PostSearchDTO) -> List[Post]:
        return self.repo.search(dto.keyword, dto.user_id, dto.status, dto.offset, dto.limit)

    def get_liked_posts(self, user_id: int, offset: int, limit: int) -> List[Post]:
        return self.repo.find_liked_by_user(user_id, offset, limit)
