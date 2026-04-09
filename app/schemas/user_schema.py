from enum import Enum
from typing import Optional, Annotated
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRole(str, Enum):
    ADMIN = "admin"
    VENDOR = "vendor"
    CUSTOMER = "customer"


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[Annotated[str, Field(max_length=255)]] = None
    role: UserRole = UserRole.CUSTOMER


class UserSignup(BaseModel):
    email: EmailStr
    full_name: Annotated[str, Field(min_length=1, max_length=100)]
    role: UserRole
    password: Annotated[str, Field(min_length=8, max_length=100)]


class UserLogin(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=1, max_length=100)]


class UserOut(UserBase):
    id: UUID
    is_active: bool
    is_verified: bool
    is_banned: bool
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
