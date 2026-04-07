from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.user_schema import UserLogin, UserOut, Token, UserSignup
from app.api.v1.crud import auth as crud_user
from app.utils.auth_utils import verify_password, create_access_token

router = APIRouter()


@router.post("/signup", response_model=UserOut)
async def signup(user: UserSignup, db: AsyncSession = Depends(get_db)):
    existing_user = await crud_user.get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud_user.create_user(db, user)


@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    found_user = await crud_user.get_user_by_email(db, email=user.email)
    if not found_user or not verify_password(user.password, found_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {
        "access_token": create_access_token(found_user.id),
        "user": found_user,
    }
