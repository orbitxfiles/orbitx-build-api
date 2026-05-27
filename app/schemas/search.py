from app.schemas.article import ArticleRead
from app.schemas.project import ProjectRead
from app.schemas.resource import ResourceRead
from app.schemas.common import OrbitXSchema


class SearchResponse(OrbitXSchema):
    articles: list[ArticleRead]
    projects: list[ProjectRead]
    resources: list[ResourceRead]
    query: str
