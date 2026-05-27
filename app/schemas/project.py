from __future__ import annotations

import enum
import re
from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator

from app.models.project import TechCategory
from app.schemas.common import OrbitXSchema


class ProjectFeatureBase(OrbitXSchema):
    title: str
    description: str | None = None
    icon: str | None = None
    order_index: int = 0


class ProjectFeatureCreate(ProjectFeatureBase):
    pass


class ProjectFeatureRead(ProjectFeatureBase):
    id: int
    project_id: int


class ProjectTechStackBase(OrbitXSchema):
    name: str
    category: TechCategory
    logo: str | None = None
    documentation_url: str | None = None


class ProjectTechStackCreate(ProjectTechStackBase):
    pass


class ProjectTechStackRead(ProjectTechStackBase):
    id: int
    project_id: int


class ProjectArchitectureNodeBase(OrbitXSchema):
    label: str
    type: str
    position_x: float = 0.0
    position_y: float = 0.0
    metadata_json: str | None = None


class ProjectArchitectureNodeCreate(ProjectArchitectureNodeBase):
    pass


class ProjectArchitectureNodeRead(ProjectArchitectureNodeBase):
    id: int
    project_id: int


class LessonLearned(OrbitXSchema):
    title: str
    body: str


class CoreFeature(OrbitXSchema):
    title: str
    description: str | None = None


class RoadmapItem(OrbitXSchema):
    milestone: str
    status: Literal["done", "in_progress", "planned"]
    date: str | None = None


_ACCENT_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

ProjectStatusLiteral = Literal["planning", "building", "launched", "archived"]
ProjectVisibilityLiteral = Literal["public", "unlisted", "private"]


class ProjectCreate(OrbitXSchema):
    # identity
    title: str
    slug: str
    tagline: str = Field(..., max_length=120)

    # content
    problem_statement: str
    architecture_overview: str
    architecture_mermaid: str | None = None

    # structured content
    lessons_learned: list[LessonLearned] | None = None
    tech_stack: list[str] | None = None
    core_features: list[CoreFeature] | None = None
    roadmap: list[RoadmapItem] | None = None

    # media & links
    thumbnail: str | None = None
    banner_image: str | None = None
    walkthrough_url: str | None = None
    walkthrough_duration: str | None = None
    github_url: str | None = None
    demo_url: str | None = None
    build_logs_url: str | None = None

    # visual identity
    accent_color: str | None = Field(default="#1a7a5e")
    icon_label: str | None = Field(default=None, max_length=2)

    # status & visibility
    status: ProjectStatusLiteral = "planning"
    is_featured: bool = False
    visibility: ProjectVisibilityLiteral = "public"

    # relations/metadata
    theme_id: int | None = None
    featured_article_ids: list[int] | None = None

    @field_validator("accent_color")
    @classmethod
    def validate_accent_color(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not _ACCENT_COLOR_RE.match(v):
            raise ValueError("accent_color must be a hex color like #1a7a5e")
        return v


class ProjectUpdate(OrbitXSchema):
    title: str | None = None
    slug: str | None = None
    tagline: str | None = Field(default=None, max_length=120)

    problem_statement: str | None = None
    architecture_overview: str | None = None
    architecture_mermaid: str | None = None

    lessons_learned: list[LessonLearned] | None = None
    tech_stack: list[str] | None = None
    core_features: list[CoreFeature] | None = None
    roadmap: list[RoadmapItem] | None = None

    thumbnail: str | None = None
    banner_image: str | None = None
    walkthrough_url: str | None = None
    walkthrough_duration: str | None = None
    github_url: str | None = None
    demo_url: str | None = None
    build_logs_url: str | None = None

    accent_color: str | None = Field(default=None)
    icon_label: str | None = Field(default=None, max_length=2)

    status: ProjectStatusLiteral | None = None
    is_featured: bool | None = None
    visibility: ProjectVisibilityLiteral | None = None

    theme_id: int | None = None
    featured_article_ids: list[int] | None = None

    @field_validator("accent_color")
    @classmethod
    def validate_accent_color(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not _ACCENT_COLOR_RE.match(v):
            raise ValueError("accent_color must be a hex color like #1a7a5e")
        return v


class ProjectRead(ProjectCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    lessons_learned: list[LessonLearned] = Field(default_factory=list)
    tech_stack: list[str] = Field(default_factory=list)
    core_features: list[CoreFeature] = Field(default_factory=list)
    roadmap: list[RoadmapItem] = Field(default_factory=list)
    featured_article_ids: list[int] = Field(default_factory=list)
    accent_color: str = "#1a7a5e"

    @field_validator(
        "lessons_learned",
        "tech_stack",
        "core_features",
        "roadmap",
        "featured_article_ids",
        mode="before",
    )
    @classmethod
    def none_to_empty_array(cls, v: object) -> object:
        if v is None:
            return []
        return v

    @field_validator("accent_color", mode="before")
    @classmethod
    def none_to_default_accent(cls, v: object) -> str:
        if v is None:
            return "#1a7a5e"
        if isinstance(v, enum.Enum):
            # should never happen, but keep normalization robust
            v = v.value
        return str(v)

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v: object) -> str:
        # support legacy DB values (beta -> building)
        if isinstance(v, enum.Enum):
            v = v.value
        if v == "beta":
            return "building"
        return str(v)

    @field_validator("visibility", mode="before")
    @classmethod
    def normalize_visibility(cls, v: object) -> str:
        # support legacy DB values (draft -> unlisted)
        if isinstance(v, enum.Enum):
            v = v.value
        if v == "draft":
            return "unlisted"
        return str(v)


class ProjectListResponse(OrbitXSchema):
    items: list[ProjectRead]
    total: int
    page: int
    page_size: int


ProjectDetailResponse = ProjectRead
