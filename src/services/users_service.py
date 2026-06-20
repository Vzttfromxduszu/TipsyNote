import re
from typing import List

from sqlalchemy.orm import Session

from dtos.users import UserCreateDTO, UserSearchDTO, UserUpdateDTO
from models.user import User
from repositories.users_repository import UsersRepository
from utils.security import hash_secret


PHONE_RE = re.compile(r"^1\d{10}$")


class UsersService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = UsersRepository(session)

    def create_user(self, dto: UserCreateDTO) -> User:
        if not PHONE_RE.match(dto.phone):
            raise ValueError("手机号格式不正确")
        if self.repo.get_by_phone(dto.phone):
            raise ValueError("手机号已存在")

        user = User(
            phone=dto.phone,
            secret=hash_secret(dto.secret),
            nickname=dto.nickname,
            avatar_url=dto.avatar_url,
            role=dto.role,
        )
        self.repo.create(user)
        self.session.commit()
        return user

    def update_user(self, user_id: int, dto: UserUpdateDTO) -> User:
        fields = {}
        if dto.nickname is not None:
            fields["nickname"] = dto.nickname
        if dto.avatar_url is not None:
            fields["avatar_url"] = dto.avatar_url
        if dto.secret is not None:
            fields["secret"] = hash_secret(dto.secret)
        if dto.status is not None:
            fields["status"] = dto.status

        user = self.repo.update(user_id, fields)
        if not user:
            raise ValueError("用户不存在")
        self.session.commit()
        return user

    def search_users(self, dto: UserSearchDTO) -> List[User]:
        return self.repo.search(dto.keyword, dto.role, dto.status, dto.offset, dto.limit)
