from pydantic import Field

from app.schemas.common import OrbitXSchema


class CategoryBase(OrbitXSchema):
    name: str
    slug: str
    description: str | None = None
    theme_id: int | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(OrbitXSchema):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    theme_id: int | None = None


class CategoryRead(CategoryBase):
    id: int
