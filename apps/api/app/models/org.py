from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Org(Base):
    __tablename__ = "orgs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    users = relationship("User", back_populates="org")
    # اگر Ticket model داری، این باید باشه تا back_populates="tickets" نخوره به دیوار:
    tickets = relationship("Ticket", back_populates="org", cascade="all, delete-orphan")
