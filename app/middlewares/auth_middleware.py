from uuid import UUID
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.utils.auth_utils import (
    AuthTokenError,
    create_access_token,
    decode_access_token,
    decode_refresh_token,
)

REFRESH_TOKEN_HEADER = "x-refresh-token"
NEW_ACCESS_TOKEN_HEADER = "X-New-Access-Token"

_SKIP_PATH_PREFIXES = (
    "/health",
    "/api/docs",
    "/openapi.json",
    "/redoc",
    "/api/v1/auth/login",
    "/api/v1/auth/signup",
)


def _should_skip_auth(path: str) -> bool:
    return any(path == p or path.startswith(p + "/") for p in _SKIP_PATH_PREFIXES)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request.state.auth = None
        request.state.auth_error = None
        request.state.new_access_token = None

        if _should_skip_auth(request.url.path):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return await call_next(request)

        access_token = auth_header[7:].strip()
        if not access_token:
            return await call_next(request)

        refresh_raw = request.headers.get(REFRESH_TOKEN_HEADER)

        try:
            payload = decode_access_token(access_token)
            try:
                request.state.auth = {
                    "user_id": UUID(payload["sub"]),
                    "role": str(payload["role"]),
                }
            except (KeyError, ValueError, TypeError):
                request.state.auth_error = {
                    "code": "token_invalid",
                    "message": "Invalid access token.",
                }
                return await call_next(request)
        except AuthTokenError as exc:
            if exc.code != "access_token_expired":
                request.state.auth_error = {"code": exc.code, "message": exc.message}
                return await call_next(request)
            if not refresh_raw:
                request.state.auth_error = {"code": exc.code, "message": exc.message}
                return await call_next(request)
            try:
                refresh_payload = decode_refresh_token(refresh_raw)
            except AuthTokenError as refresh_exc:
                request.state.auth_error = {
                    "code": refresh_exc.code,
                    "message": refresh_exc.message,
                }
                return await call_next(request)
            try:
                user_id = UUID(refresh_payload["sub"])
                role = str(refresh_payload["role"])
            except (KeyError, ValueError, TypeError):
                request.state.auth_error = {
                    "code": "session_expired",
                    "message": "You have been logged out. Please log in again.",
                }
                return await call_next(request)
            request.state.new_access_token = create_access_token(user_id, role)
            request.state.auth = {"user_id": user_id, "role": role}

        response = await call_next(request)
        new_token = getattr(request.state, "new_access_token", None)
        if new_token:
            response.headers[NEW_ACCESS_TOKEN_HEADER] = new_token
        return response
