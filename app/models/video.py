import enum

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class VideoPlatform(str, enum.Enum):
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    LOOM = "loom"
    LOCAL = "local"


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    video_url: Mapped[str] = mapped_column(String(512), nullable=False)
    thumbnail: Mapped[str | None] = mapped_column(String(512))
    platform: Mapped[VideoPlatform] = mapped_column(
        Enum(VideoPlatform, name="video_platform", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    duration: Mapped[int | None] = mapped_column(Integer)

    article_id: Mapped[int | None] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"))
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))

    article = relationship("Article", back_populates="videos")
    project = relationship("Project", back_populates="videos")
