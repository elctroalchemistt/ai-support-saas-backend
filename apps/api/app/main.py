from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import Base, engine

# import models to register mappers
from app import models  # noqa: F401

from app.routers.auth import router as auth_router
from app.routers.orgs import router as orgs_router
from app.routers.tickets import router as tickets_router


def _cors_origins() -> list[str]:
    """
    settings.CORS_ORIGINS ممکنه list باشه یا str (اگر کسی comma-separated بده).
    این تابع همیشه list برمی‌گردونه تا CORSMiddleware بدون دردسر کار کنه.
    """
    origins = settings.CORS_ORIGINS
    if isinstance(origins, list):
        return origins
    if not origins:
        return []
    # allow comma-separated fallback
    return [o.strip() for o in origins.split(",") if o.strip()]


app = FastAPI(title="AI Support SaaS API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(orgs_router)
app.include_router(tickets_router)


@app.on_event("startup")
def _startup():
    """
    نکته مهم:
    - برای DEV خوبه که جدول‌ها خودکار ساخته بشن.
    - ولی وقتی با Alembic کار می‌کنی، بهتره در prod غیرفعال باشه.
    """
    if getattr(settings, "ENV", "dev") == "dev":
        Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"ok": True}
