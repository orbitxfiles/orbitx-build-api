import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    BUILDING = "building"
    BETA = "beta"
    LAUNCHED = "launched"
    ARCHIVED = "archived"


class ProjectVisibility(str, enum.Enum):
    PUBLIC = "public"
    DRAFT = "draft"
    UNLISTED = "unlisted"
    PRIVATE = "private"


class TechCategory(str, enum.Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    AI = "ai"
    INFRA = "infra"
    DATABASE = "database"
    DEPLOYMENT = "deployment"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    short_description: Mapped[str | None] = mapped_column(Text)
    tagline: Mapped[str] = mapped_column(String(120), nullable=False)
    full_description: Mapped[str | None] = mapped_column(Text)
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    architecture_overview: Mapped[str] = mapped_column(Text, nullable=False)
    architecture_mermaid: Mapped[str | None] = mapped_column(Text)
    lessons_learned: Mapped[list[dict] | None] = mapped_column(JSON)
    github_url: Mapped[str | None] = mapped_column(String(512))
    demo_url: Mapped[str | None] = mapped_column(String(512))
    thumbnail: Mapped[str | None] = mapped_column(String(512))
    banner_image: Mapped[str | None] = mapped_column(String(512))
    tech_stack: Mapped[list[str] | None] = mapped_column(JSON)
    core_features: Mapped[list[dict] | None] = mapped_column(JSON)
    roadmap: Mapped[list[dict] | None] = mapped_column(JSON)
    walkthrough_url: Mapped[str | None] = mapped_column(String(512))
    walkthrough_duration: Mapped[str | None] = mapped_column(String(64))
    build_logs_url: Mapped[str | None] = mapped_column(String(512))

    theme_id: Mapped[int | None] = mapped_column(ForeignKey("themes.id", ondelete="SET NULL"))
    featured_article_id: Mapped[int | None] = mapped_column(
        ForeignKey("articles.id", ondelete="SET NULL", use_alter=True, name="fk_project_featured_article")
    )
    featured_article_ids: Mapped[list[int] | None] = mapped_column(JSON)
    accent_color: Mapped[str | None] = mapped_column(String(7), default="#1a7a5e")
    icon_label: Mapped[str | None] = mapped_column(String(2))

    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status", values_callable=lambda x: [e.value for e in x]),
        default=ProjectStatus.PLANNING,
        nullable=False,
    )
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    visibility: Mapped[ProjectVisibility] = mapped_column(
        Enum(ProjectVisibility, name="project_visibility", values_callable=lambda x: [e.value for e in x]),
        default=ProjectVisibility.PUBLIC,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    theme = relationship("Theme", back_populates="projects")
    features = relationship(
        "ProjectFeature", back_populates="project", cascade="all, delete-orphan"
    )
    tech_stack_rows = relationship(
        "ProjectTechStack", back_populates="project", cascade="all, delete-orphan"
    )
    architecture_nodes = relationship(
        "ProjectArchitectureNode", back_populates="project", cascade="all, delete-orphan"
    )
    articles = relationship("Article", back_populates="project", foreign_keys="Article.project_id")
    videos = relationship("Video", back_populates="project")
    resources = relationship("Resource", back_populates="project")


class ProjectFeature(Base):
    __tablename__ = "project_features"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str | None] = mapped_column(String(128))
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    project = relationship("Project", back_populates="features")


class ProjectTechStack(Base):
    __tablename__ = "project_tech_stack"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[TechCategory] = mapped_column(
        Enum(TechCategory, name="tech_category", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    logo: Mapped[str | None] = mapped_column(String(512))
    documentation_url: Mapped[str | None] = mapped_column(String(512))

    project = relationship("Project", back_populates="tech_stack_rows")


class ProjectArchitectureNode(Base):
    __tablename__ = "project_architecture_nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    position_x: Mapped[float] = mapped_column(default=0.0)
    position_y: Mapped[float] = mapped_column(default=0.0)
    metadata_json: Mapped[str | None] = mapped_column(Text)

    project = relationship("Project", back_populates="architecture_nodes")
