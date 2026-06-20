from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from api.pubs import _to_pub_response
from schema.schemas import SendCodeRequest
from schema.schemas_auth import LoginRequest, TokenResponse, CurrentUserResponse
from services.auth_service import AuthService
from services.pubs_service import PubsService
from utils.jwt_utils import create_access_token
from utils.avatar_url import normalize_avatar_url
from utils.sms import send_verification_code


router = APIRouter(tags=["auth"])


@router.post("/auth/send-code")
def send_code(payload: SendCodeRequest):
    send_verification_code(payload.phone)
    return {"message": "验证码已发送"}


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.authenticate(payload.phone, payload.secret)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=CurrentUserResponse)
def me(user=Depends(get_current_user), db: Session = Depends(get_db)):
    service = PubsService(db)
    managed = service.get_managed_pubs(user.role, user.id)
    return {
        "id": user.id,
        "phone": user.phone,
        "nickname": user.nickname,
        "avatar_url": normalize_avatar_url(user.avatar_url),
        "role": user.role,
        "status": user.status,
        "managed_pubs": [_to_pub_response(p) for p in managed],
    }
