from sqlalchemy.orm import Session

from repositories.users_repository import UsersRepository
from utils.security import verify_secret


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = UsersRepository(session)

    def authenticate(self, phone: str, secret: str):
        user = self.repo.get_by_phone(phone)
        if not user:
            return None
        if not verify_secret(secret, user.secret):
            return None
        if user.status == 0:
            return None
        return user
