from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt

from configs.settings import settings


def create_access_token(payload: Dict[str, Any]) -> str:
    secret = settings.jwt_secret
    algorithm = settings.jwt_algorithm
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=settings.token_expire_minutes)
    to_encode = {**payload, "exp": expire_at}
    return jwt.encode(to_encode, secret, algorithm=algorithm)


def decode_access_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
