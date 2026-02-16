from pydantic import BaseModel, EmailStr
from src.models.users import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    role: UserRole = UserRole.CUSTOMER


class Token(BaseModel):
    access_token: str
    token_type: str
