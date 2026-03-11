from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, default_limits=["100 per 15 minutes"])


def rate_limit_handler(request: Request, exc: Exception) -> JSONResponse:
    details = None
    if isinstance(exc, RateLimitExceeded):
        details = exc.detail
    return JSONResponse(
        status_code=429,
        content={
            "status": "error",
            "code": "too_many_requests",
            "message": "Rate limit exceeded. Please try again later.",
            "details": details,
        },
    )
