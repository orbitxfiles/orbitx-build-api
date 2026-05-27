from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Theme(Base):
    __tablename__ = "themes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    primary_color: Mapped[str] = mapped_column(String(32), default="#22c55e")
    secondary_color: Mapped[str] = mapped_column(String(32), default="#16a34a")
    accent_color: Mapped[str] = mapped_column(String(32), default="#4ade80")
    background_color: Mapped[str] = mapped_column(String(32), default="#0a0f0a")
    text_color: Mapped[str] = mapped_column(String(32), default="#e5e7eb")
    strong_text_color: Mapped[str] = mapped_column(String(32), default="#ffffff")
    muted_text_color: Mapped[str] = mapped_column(String(32), default="#9ca3af")
    border_color: Mapped[str] = mapped_column(String(32), default="#1f2937")

    heading_font: Mapped[str] = mapped_column(String(128), default="Inter")
    body_font: Mapped[str] = mapped_column(String(128), default="Inter")
    serif_font: Mapped[str | None] = mapped_column(String(128))

    button_radius: Mapped[str] = mapped_column(String(32), default="0.5rem")
    card_radius: Mapped[str] = mapped_column(String(32), default="0.75rem")
    shadow_style: Mapped[str | None] = mapped_column(String(255))

    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    projects = relationship("Project", back_populates="theme")
    articles = relationship("Article", back_populates="theme")
    categories = relationship("Category", back_populates="theme")
