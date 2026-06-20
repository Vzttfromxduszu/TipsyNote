from typing import Optional
from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from schema.schemas import (
    UserCreateRequest,
    UserUpdateRequest,
    UserCreateResponse,
    UserSearchResponse,
)
from dtos.users import UserCreateDTO, UserUpdateDTO, UserSearchDTO
from services.users_service import UsersService
from configs.settings import settings
from utils.avatar_url import normalize_avatar_url
from utils.amap_geocode import reverse_geocode
from utils.sms import verify_code


router = APIRouter(tags=["users"])


@router.post("/users", response_model=UserCreateResponse)
def create_user(payload: UserCreateRequest, db: Session = Depends(get_db)):
    if not verify_code(payload.phone, payload.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误或已过期")
    service = UsersService(db)
    try:
        dto = UserCreateDTO(**payload.model_dump(exclude={"code"}))
        user = service.create_user(dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {"id": user.id, "phone": user.phone, "nickname": user.nickname}


@router.put("/users/{user_id}")
def update_user(user_id: int, payload: UserUpdateRequest, db: Session = Depends(get_db)):
    service = UsersService(db)
    user = service.update_user(user_id, UserUpdateDTO(**payload.model_dump()))
    return {"id": user.id, "phone": user.phone, "nickname": user.nickname}


@router.get("/users", response_model=UserSearchResponse)
def search_users(
    keyword: Optional[str] = None,
    role: Optional[int] = None,
    status: Optional[int] = None,
    offset: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    service = UsersService(db)
    dto = UserSearchDTO(keyword=keyword, role=role, status=status, offset=offset, limit=limit)
    users = service.search_users(dto)
    return {
        "items": [
            {"id": u.id, "phone": u.phone, "nickname": u.nickname, "role": u.role}
            for u in users
        ],
        "offset": offset,
        "limit": limit,
    }


@router.post("/users/me/avatar")
def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 JPG/PNG")
    content = file.file.read()
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="图片需小于 2MB")
    storage_root = Path(settings.storage_path)
    avatar_dir = storage_root / "avatars"
    avatar_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = avatar_dir / filename
    with filepath.open("wb") as f:
        f.write(content)
    # 存储相对 URL，前端可直接通过 /api/avatars/{filename} 访问
    avatar_url = f"/api/avatars/{filename}"
    service = UsersService(db)
    user = service.update_user(current_user.id, UserUpdateDTO(avatar_url=avatar_url))
    return {"avatar_url": normalize_avatar_url(user.avatar_url)}

