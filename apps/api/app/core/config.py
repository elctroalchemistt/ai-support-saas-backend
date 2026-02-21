from __future__ import annotations

import json
from typing import List

from pydantic import Field, AliasChoices, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",          # مهم: با env های اضافی crash نکنه
        case_sensitive=False,
    )

    ENV: str = "dev"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    DATABASE_URL: str

    # JWT / Cookies
    SECRET_KEY: str = Field(
        default="dev-secret-change-me",
        validation_alias=AliasChoices("SECRET_KEY", "JWT_SECRET"),
    )
    JWT_ALG: str = Field(default="HS256", validation_alias=AliasChoices("JWT_ALG", "JWT_ALGORITHM"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    ACCESS_COOKIE_NAME: str = "access_token"
    REFRESH_COOKIE_NAME: str = "refresh_token"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"  # "lax" | "strict" | "none"

    # CORS: هم "http://localhost:3000" هم "a,b" هم '["a","b"]' رو قبول کنه
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    REDIS_URL: str = "redis://redis:6379/0"
    RATE_LIMIT_AI_PER_MINUTE: int = 20

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if v is None:
            return ["http://localhost:3000"]
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return ["http://localhost:3000"]
            # اگر JSON list بود
            if s.startswith("["):
                try:
                    data = json.loads(s)
                    if isinstance(data, list):
                        return [str(x).strip() for x in data if str(x).strip()]
                except Exception:
                    pass
            # اگر comma-separated بود
            return [x.strip() for x in s.split(",") if x.strip()]
        return v


settings = Settings()
