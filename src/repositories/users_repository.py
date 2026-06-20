from typing import List, Optional

from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from models.user import User


class UsersRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.get(User, user_id)

    def get_by_phone(self, phone: str) -> Optional[User]:
        stmt = select(User).where(User.phone == phone)
        return self.session.execute(stmt).scalars().first()

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        return user

    def update(self, user_id: int, fields: dict) -> Optional[User]:
        if not fields:
            return self.get_by_id(user_id)
        stmt = update(User).where(User.id == user_id).values(**fields)
        self.session.execute(stmt)
        return self.get_by_id(user_id)

    def search(
        self,
        keyword: Optional[str],
        role: Optional[int],
        status: Optional[int],
        offset: int,
        limit: int,
    ) -> List[User]:
        stmt = select(User)
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(or_(User.phone.like(like), User.nickname.like(like)))
        if role is not None:
            stmt = stmt.where(User.role == role)
        if status is not None:
            stmt = stmt.where(User.status == status)
        stmt = stmt.offset(offset).limit(limit)
        return list(self.session.execute(stmt).scalars().all())
