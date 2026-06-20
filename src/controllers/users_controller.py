from typing import Dict, Any

from db.session import get_session_factory
from dtos.users import UserCreateDTO, UserSearchDTO, UserUpdateDTO
from services.users_service import UsersService


SessionLocal = get_session_factory()


def create_user(payload: Dict[str, Any]) -> Dict[str, Any]:
    dto = UserCreateDTO(**payload)
    with SessionLocal() as session:
        service = UsersService(session)
        user = service.create_user(dto)
        return {"id": user.id, "phone": user.phone, "nickname": user.nickname}


def update_user(user_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    dto = UserUpdateDTO(**payload)
    with SessionLocal() as session:
        service = UsersService(session)
        user = service.update_user(user_id, dto)
        return {"id": user.id, "phone": user.phone, "nickname": user.nickname}


def search_users(query: Dict[str, Any]) -> Dict[str, Any]:
    dto = UserSearchDTO(**query)
    with SessionLocal() as session:
        service = UsersService(session)
        users = service.search_users(dto)
        return {
            "items": [
                {"id": u.id, "phone": u.phone, "nickname": u.nickname, "role": u.role}
                for u in users
            ],
            "offset": dto.offset,
            "limit": dto.limit,
        }
