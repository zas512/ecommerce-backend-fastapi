from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.crud import get_user_by_email, create_user
from app.core.db import get_db
from app.schemas.user_schema import UserLogin, UserOut, Token, UserSignup
from app.utils.auth_utils import (
    create_access_token,
    create_refresh_token,
    verify_password,
)

router = APIRouter()


@router.post("/signup", response_model=UserOut)
async def signup(user: UserSignup, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await create_user(db, user)


@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    found_user = await get_user_by_email(db, email=user.email)
    if not found_user or not verify_password(user.password, found_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    role = found_user.role.value
    return {
        "access_token": create_access_token(found_user.id, role),
        "refresh_token": create_refresh_token(found_user.id, role),
        "user": found_user,
    }
