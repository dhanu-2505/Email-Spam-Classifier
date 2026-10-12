import jwt
from fastapi import Cookie, HTTPException

from app.config import AUTH_COOKIE_NAME
from app.services.auth_service import decode_token


def require_user(session: str | None = Cookie(default=None, alias=AUTH_COOKIE_NAME)) -> str:
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required.")
    try:
        return decode_token(session)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")
