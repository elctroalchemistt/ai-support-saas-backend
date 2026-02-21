from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

import bcrypt
from fastapi import HTTPException, Request, Depends
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.models.user import User


# ---- Password ----
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ---- JWT ----
def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(claims: Dict[str, Any]) -> str:
    to_encode = dict(claims)
    expire = _now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "typ": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALG)


def create_refresh_token(claims: Dict[str, Any]) -> tuple[str, str]:
    to_encode = dict(claims)
    expire = _now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    jti = uuid4().hex
    to_encode.update({"exp": expire, "typ": "refresh", "jti": jti})
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALG)
    return token, jti


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALG])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def hash_jti(jti: str) -> str:
    return hashlib.sha256(jti.encode("utf-8")).hexdigest()


# ---- Cookies ----
def set_auth_cookies(response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.ACCESS_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )


def clear_auth_cookies(response) -> None:
    response.delete_cookie(settings.ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/")


# ---- Current user ----
def _get_bearer(request: Request) -> Optional[str]:
    auth = request.headers.get("Authorization") or ""
    if auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    return None


def get_current_user_from_request(request: Request, db: Session) -> User:
    token = request.cookies.get(settings.ACCESS_COOKIE_NAME) or _get_bearer(request)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_token(token)
    if payload.get("typ") != "access":
        raise HTTPException(status_code=401, detail="Invalid access token")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.get(User, int(sub))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_user(request: Request, db: Session = Depends(get_db)) -> User:
    return get_current_user_from_request(request, db)
