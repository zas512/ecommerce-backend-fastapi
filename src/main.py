from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import get_db
from sqlalchemy import text
from src.routes.auth import router as auth_router


app = FastAPI()
app.include_router(auth_router)


@app.get("/")
async def root():
    return {"message": "API is running"}


@app.get("/ping-db")
async def ping_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"db": result.scalar()}
