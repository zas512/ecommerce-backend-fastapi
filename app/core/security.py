from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
import secure

limiter = Limiter(key_func=get_remote_address, default_limits=["100 per 15 minutes"])


def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "status": "error",
            "code": "too_many_requests",
            "message": "Rate limit exceeded. Please try again later.",
            "details": exc.detail,
        },
    )


hsts = secure.StrictTransportSecurity().max_age(31536000).include_subdomains()
referrer = secure.ReferrerPolicy().no_referrer()
cache_control = secure.CacheControl().no_cache().no_store().must_revalidate()
x_frame_options = secure.XFrameOptions().deny()

secure_headers = secure.Secure(
    hsts=hsts, referrer=referrer, cache=cache_control, xfo=x_frame_options
)
