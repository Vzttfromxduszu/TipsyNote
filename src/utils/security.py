from passlib.context import CryptContext


_pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_secret(secret: str) -> str:
    return _pwd_context.hash(secret)


def verify_secret(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)
