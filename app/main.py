from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.db import check_db_connection
from app.core.logger import logger
from slowapi.errors import RateLimitExceeded
from app.core.security import limiter, rate_limit_handler, secure_headers
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.core.config import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Initializing application startup...")
    await check_db_connection()
    yield
    logger.info("Shutting down application...")


def get_application() -> FastAPI:
    _app = FastAPI(
        title="Multi-Vendor E-Commerce API",
        description="Multi-Vendor E-Commerce API",
        version="1.0.0",
        docs_url="/api/docs",
        lifespan=lifespan,
    )
    _app.state.limiter = limiter
    _app.add_middleware(SlowAPIMiddleware)
    _app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

    @_app.middleware("http")
    async def set_secure_headers(request: Request, call_next):
        response = await call_next(request)
        secure_headers.framework.fastapi(response)
        return response

    _app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
    _app.add_middleware(GZipMiddleware, minimum_size=1000)
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _app.include_router(api_router, prefix="/api/v1")
    return _app


app = get_application()


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "online",
        "message": "Server is running",
        "environment": settings.ENV_MODE,
    }
