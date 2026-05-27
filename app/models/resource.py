import enum

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ResourceType(str, enum.Enum):
    PDF = "pdf"
    TEMPLATE = "template"
    CHEAT_SHEET = "cheat_sheet"
    SOURCE_CODE = "source_code"
    ARCHITECTURE_DOC = "architecture_doc"


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    file_url: Mapped[str] = mapped_column(String(512), nullable=False)
    type: Mapped[ResourceType] = mapped_column(
        Enum(ResourceType, name="resource_type", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    thumbnail: Mapped[str | None] = mapped_column(String(512))

    article_id: Mapped[int | None] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"))
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))

    article = relationship("Article", back_populates="resources")
    project = relationship("Project", back_populates="resources")
