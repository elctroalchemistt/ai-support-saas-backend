from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import (
    clear_auth_cookies,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user_from_request,
    hash_jti,
    hash_password,
    set_auth_cookies,
    verify_password,
)
from app.models.org import Org
from app.models.refresh_token import RefreshToken
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc_aware(dt: datetime) -> datetime:
    if dt is None:
        return None  # type: ignore[return-value]
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


# -------- schemas (inline) --------

class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=200)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)


class MeOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


# -------- helpers --------

def _ensure_user_has_org(db: Session, user: User) -> User:
    """
    Safety net for old users: if org_id is NULL, create an org and attach it.
    """
    if getattr(user, "org_id", None):
        return user

    org = Org(name=f"{user.email.split('@')[0]}'s org")
    db.add(org)
    db.flush()  # org.id

    user.org_id = org.id  # type: ignore[attr-defined]
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# -------- routes --------

@router.post("/signup", response_model=MeOut)
def signup(payload: SignupIn, response: Response, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=400, detail="Email already in use")

    # 1) create org first
    org = Org(name=f"{payload.email.split('@')[0]}'s org")
    db.add(org)
    db.flush()  # get org.id without committing yet

    # 2) create user with org_id
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        org_id=org.id,  # <-- critical
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access = create_access_token({"sub": str(user.id)})
    refresh, jti = create_refresh_token({"sub": str(user.id)})

    rt = RefreshToken(
        user_id=user.id,
        jti_hash=hash_jti(jti),
        expires_at=_utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked=False,
    )
    db.add(rt)
    db.commit()

    set_auth_cookies(response, access, refresh)
    return user


@router.post("/login", response_model=MeOut)
def login(payload: LoginIn, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # ensure org_id exists (fix for previously-created users)
    user = _ensure_user_has_org(db, user)

    access = create_access_token({"sub": str(user.id)})
    refresh, jti = create_refresh_token({"sub": str(user.id)})

    rt = RefreshToken(
        user_id=user.id,
        jti_hash=hash_jti(jti),
        expires_at=_utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked=False,
    )
    db.add(rt)
    db.commit()

    set_auth_cookies(response, access, refresh)
    return user


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if token:
        try:
            payload = decode_token(token)
            jti = payload.get("jti")
            if jti:
                jh = hash_jti(jti)
                rt = db.scalar(select(RefreshToken).where(RefreshToken.jti_hash == jh))
                if rt:
                    rt.revoked = True
                    db.commit()
        except Exception:
            pass

    clear_auth_cookies(response)
    return {"ok": True}


@router.get("/me", response_model=MeOut)
def me(request: Request, db: Session = Depends(get_db)):
    return get_current_user_from_request(request, db)


@router.post("/refresh")
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    payload = decode_token(token)
    if payload.get("typ") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    sub = payload.get("sub")
    jti = payload.get("jti")
    if not sub or not jti:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    jh = hash_jti(jti)
    rt = db.scalar(select(RefreshToken).where(RefreshToken.jti_hash == jh))

    now = _utcnow()
    expires_at = _as_utc_aware(rt.expires_at) if rt else None

    if (not rt) or rt.revoked or (expires_at is not None and expires_at < now):
        raise HTTPException(status_code=401, detail="Refresh token revoked/expired")

    rt.revoked = True

    user = db.query(User).filter(User.id == int(sub)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    # ensure org_id exists even on refresh
    user = _ensure_user_has_org(db, user)

    access = create_access_token({"sub": str(user.id)})
    new_refresh, new_jti = create_refresh_token({"sub": str(user.id)})

    new_rt = RefreshToken(
        user_id=user.id,
        jti_hash=hash_jti(new_jti),
        expires_at=_utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked=False,
    )

    db.add(new_rt)
    db.commit()

    set_auth_cookies(response, access, new_refresh)
    return {"ok": True}
