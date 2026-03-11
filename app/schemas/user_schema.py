from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    VENDOR = "vendor"
    CUSTOMER = "customer"


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[Annotated[str, Field(max_length=255)]] = None
    role: UserRole = UserRole.CUSTOMER


class UserCreate(UserBase):
    password: Annotated[str, Field(min_length=8, max_length=100)]


class UserOut(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    is_banned: bool
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenPayload(BaseModel):
    sub: Optional[str] = None
