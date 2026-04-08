import secrets

from fastapi import HTTPException, Request, status
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], default="bcrypt_sha256", deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def set_user_session(request: Request, user_id: int, role: str, username: str) -> None:
    request.session["user_id"] = user_id
    request.session["role"] = role
    request.session["username"] = username


def clear_user_session(request: Request) -> None:
    request.session.clear()


def get_csrf_token(request: Request) -> str:
    token = request.session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(24)
        request.session["csrf_token"] = token
    return token


def enforce_csrf(request: Request, token: str | None) -> None:
    expected = request.session.get("csrf_token")
    if not expected or not token or expected != token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token")
