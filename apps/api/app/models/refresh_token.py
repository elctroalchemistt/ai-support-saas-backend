from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.core.db import Base


def utcnow() -> datetime:
    # timezone-aware UTC
    return datetime.now(timezone.utc)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    jti_hash = Column(String(64), nullable=False, unique=True, index=True)

    # مهم: timezone-aware
    expires_at = Column(DateTime(timezone=True), nullable=False)

    revoked = Column(Boolean, default=False, nullable=False)

    # مهم: timezone-aware
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")
