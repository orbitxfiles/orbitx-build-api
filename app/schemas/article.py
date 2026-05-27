from datetime import datetime

from pydantic import Field

from app.models.article import ContentVisibility, SectionType
from app.schemas.auth import UserRead
from app.schemas.common import OrbitXSchema
from app.schemas.theme import ThemeRead
from app.schemas.video import VideoRead
from app.schemas.resource import ResourceRead


class ArticleSectionBase(OrbitXSchema):
    section_type: SectionType
    title: str | None = None
    content: str | None = None
    order_index: int = 0


class ArticleSectionCreate(ArticleSectionBase):
    pass


class ArticleSectionRead(ArticleSectionBase):
    id: int
    article_id: int


class ArticleBase(OrbitXSchema):
    title: str
    slug: str
    excerpt: str | None = None
    content_markdown: str | None = None
    cover_image: str | None = None
    reading_time: int | None = None
    category_id: int | None = None
    theme_id: int | None = None
    author_id: int | None = None
    project_id: int | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    seo_keywords: str | None = None
    featured: bool = False
    published: bool = False
    visibility: ContentVisibility = ContentVisibility.DRAFT


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(OrbitXSchema):
    title: str | None = None
    slug: str | None = None
    excerpt: str | None = None
    content_markdown: str | None = None
    cover_image: str | None = None
    reading_time: int | None = None
    category_id: int | None = None
    theme_id: int | None = None
    author_id: int | None = None
    project_id: int | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    seo_keywords: str | None = None
    featured: bool | None = None
    published: bool | None = None
    visibility: ContentVisibility | None = None


class ArticleRead(ArticleBase):
    id: int
    created_at: datetime
    updated_at: datetime


class ArticleListResponse(OrbitXSchema):
    items: list[ArticleRead]
    total: int
    page: int
    page_size: int


class ArticleDetailResponse(ArticleRead):
    sections: list[ArticleSectionRead] = []
    author: UserRead | None = None
    theme: ThemeRead | None = None
    resources: list[ResourceRead] = []
    videos: list[VideoRead] = []
    related_articles: list[ArticleRead] = []
