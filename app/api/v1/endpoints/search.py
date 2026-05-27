from fastapi import APIRouter, Query
from sqlalchemy import or_, select

from app.core.deps import DbSession
from app.models.article import Article, ContentVisibility
from app.models.project import Project, ProjectVisibility
from app.models.resource import Resource
from app.schemas.search import SearchResponse

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def search(db: DbSession, q: str = Query(..., min_length=1)):
    pattern = f"%{q}%"

    articles = list(
        db.scalars(
            select(Article)
            .where(
                Article.published.is_(True),
                Article.visibility == ContentVisibility.PUBLIC,
                or_(
                    Article.title.ilike(pattern),
                    Article.excerpt.ilike(pattern),
                    Article.content_markdown.ilike(pattern),
                ),
            )
            .limit(20)
        ).all()
    )

    projects = list(
        db.scalars(
            select(Project)
            .where(
                Project.visibility == ProjectVisibility.PUBLIC,
                or_(
                    Project.title.ilike(pattern),
                    Project.tagline.ilike(pattern),
                    Project.full_description.ilike(pattern),
                ),
            )
            .limit(20)
        ).all()
    )

    resources = list(
        db.scalars(
            select(Resource).where(
                or_(
                    Resource.title.ilike(pattern),
                    Resource.description.ilike(pattern),
                )
            ).limit(20)
        ).all()
    )

    return SearchResponse(
        query=q,
        articles=articles,
        projects=projects,
        resources=resources,
    )
