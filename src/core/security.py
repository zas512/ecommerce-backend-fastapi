from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from src.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(pwd: str) -> str:
    return pwd_context.hash(pwd)


def verify_password(pwd: str, hashed: str) -> bool:
    return pwd_context.verify(pwd, hashed)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
