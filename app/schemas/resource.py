from app.models.resource import ResourceType
from app.schemas.common import OrbitXSchema


class ResourceBase(OrbitXSchema):
    title: str
    description: str | None = None
    file_url: str
    type: ResourceType
    thumbnail: str | None = None
    article_id: int | None = None
    project_id: int | None = None


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(OrbitXSchema):
    title: str | None = None
    description: str | None = None
    file_url: str | None = None
    type: ResourceType | None = None
    thumbnail: str | None = None
    article_id: int | None = None
    project_id: int | None = None


class ResourceRead(ResourceBase):
    id: int
