from fastapi import HTTPException, Request
from app.schemas.auth_schema import JwtIdentity


async def get_current_user(request: Request) -> JwtIdentity:
    auth_error = getattr(request.state, "auth_error", None)
    if auth_error:
        raise HTTPException(
            status_code=401,
            detail={
                "code": auth_error["code"],
                "message": auth_error["message"],
            },
        )
    auth = getattr(request.state, "auth", None)
    if not auth:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "not_authenticated",
                "message": "Not authenticated. Send Authorization: Bearer <access_token>.",
            },
        )
    return JwtIdentity(id=auth["user_id"], role=auth["role"])
