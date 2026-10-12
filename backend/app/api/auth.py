import jwt
from fastapi import APIRouter, Cookie, HTTPException, Response, status

from app.config import (
    AUTH_COOKIE_NAME,
    AUTH_COOKIE_SAMESITE,
    AUTH_COOKIE_SECURE,
    AUTH_TOKEN_MINUTES,
)
from app.schemas import LoginRequest, RegisterRequest
from app.services.auth_service import authenticate_user, create_token, decode_token, register_user

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register")
def register(payload: RegisterRequest):
    if not register_user(payload.email, payload.password):
        raise HTTPException(status_code=409, detail="An account with that email already exists.")
    return {"message": "Account created. You can now log in."}


@router.post("/login")
def login(payload: LoginRequest, response: Response):
    if not authenticate_user(payload.email, payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    response.set_cookie(
        AUTH_COOKIE_NAME,
        create_token(payload.email),
        httponly=True,
        secure=AUTH_COOKIE_SECURE,
        samesite=AUTH_COOKIE_SAMESITE,
        max_age=AUTH_TOKEN_MINUTES * 60,
        path="/",
    )
    return {"authenticated": True, "email": payload.email.strip().lower()}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        AUTH_COOKIE_NAME,
        secure=AUTH_COOKIE_SECURE,
        httponly=True,
        samesite=AUTH_COOKIE_SAMESITE,
        path="/",
    )
    return {"authenticated": False}


@router.get("/me")
def me(session: str | None = Cookie(default=None, alias=AUTH_COOKIE_NAME)):
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required.")
    try:
        email = decode_token(session)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")
    return {"authenticated": True, "email": email}
