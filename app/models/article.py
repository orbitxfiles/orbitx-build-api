import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ContentVisibility(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    DRAFT = "draft"


class SectionType(str, enum.Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    CODE = "code"
    IMAGE = "image"
    DIAGRAM = "diagram"
    VIDEO = "video"
    QUOTE = "quote"
    ARCHITECTURE = "architecture"
    TWEET_EMBED = "tweet_embed"


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    excerpt: Mapped[str | None] = mapped_column(Text)
    content_markdown: Mapped[str | None] = mapped_column(Text)
    cover_image: Mapped[str | None] = mapped_column(String(512))
    reading_time: Mapped[int | None] = mapped_column(Integer)

    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    theme_id: Mapped[int | None] = mapped_column(ForeignKey("themes.id", ondelete="SET NULL"))
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"))

    seo_title: Mapped[str | None] = mapped_column(String(255))
    seo_description: Mapped[str | None] = mapped_column(Text)
    seo_keywords: Mapped[str | None] = mapped_column(String(512))

    featured: Mapped[bool] = mapped_column(Boolean, default=False)
    published: Mapped[bool] = mapped_column(Boolean, default=False)
    visibility: Mapped[ContentVisibility] = mapped_column(
        Enum(ContentVisibility, name="content_visibility", values_callable=lambda x: [e.value for e in x]),
        default=ContentVisibility.DRAFT,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    category = relationship("Category", back_populates="articles")
    theme = relationship("Theme", back_populates="articles")
    author = relationship("User", back_populates="articles")
    project = relationship(
        "Project", back_populates="articles", foreign_keys=[project_id]
    )
    sections = relationship(
        "ArticleSection", back_populates="article", cascade="all, delete-orphan", order_by="ArticleSection.order_index"
    )
    videos = relationship("Video", back_populates="article")
    resources = relationship("Resource", back_populates="article")
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")


class ArticleSection(Base):
    __tablename__ = "article_sections"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    section_type: Mapped[SectionType] = mapped_column(
        Enum(SectionType, name="section_type", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(255))
    content: Mapped[str | None] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    article = relationship("Article", back_populates="sections")
