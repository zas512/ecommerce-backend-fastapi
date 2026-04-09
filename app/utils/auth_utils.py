import hashlib
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
from jose import JWTError, ExpiredSignatureError, jwt
from app.core.config import settings


class AuthTokenError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def hash_password(password: str) -> str:
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    hashed = bcrypt.hashpw(digest.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    digest = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return bcrypt.checkpw(
        digest.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(
    user_id: Union[str, Any],
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.ACCESS_TOKEN_EXPIRE_DAYS
        )
    to_encode = {
        "exp": expire,
        "sub": str(user_id),
        "role": role,
        "type": "access",
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def create_refresh_token(
    user_id: Union[str, Any],
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    to_encode = {
        "exp": expire,
        "sub": str(user_id),
        "role": role,
        "type": "refresh",
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def _validate_access_payload(payload: dict) -> None:
    if payload.get("type") == "refresh":
        raise AuthTokenError("token_invalid", "Invalid access token.")
    if not payload.get("role"):
        raise AuthTokenError("token_invalid", "Invalid access token.")


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        raise AuthTokenError(
            "access_token_expired",
            "Access token expired. Send X-Refresh-Token to obtain a new access token.",
        )
    except JWTError:
        raise AuthTokenError("token_invalid", "Invalid access token.")
    _validate_access_payload(payload)
    return payload


def decode_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        raise AuthTokenError(
            "session_expired",
            "You have been logged out. Please log in again.",
        )
    except JWTError:
        raise AuthTokenError(
            "session_expired",
            "You have been logged out. Please log in again.",
        )
    if payload.get("type") != "refresh":
        raise AuthTokenError(
            "session_expired",
            "You have been logged out. Please log in again.",
        )
    if not payload.get("role"):
        raise AuthTokenError(
            "session_expired",
            "You have been logged out. Please log in again.",
        )
    return payload
