from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class KBArticle(Base):
    __tablename__ = "kb_articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    body: Mapped[str] = mapped_column(String(20000))
    tags_csv: Mapped[str] = mapped_column(String(1000), default="")
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
