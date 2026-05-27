from app.models.video import VideoPlatform
from app.schemas.common import OrbitXSchema


class VideoBase(OrbitXSchema):
    title: str
    video_url: str
    thumbnail: str | None = None
    platform: VideoPlatform
    duration: int | None = None
    article_id: int | None = None
    project_id: int | None = None


class VideoCreate(VideoBase):
    pass


class VideoUpdate(OrbitXSchema):
    title: str | None = None
    video_url: str | None = None
    thumbnail: str | None = None
    platform: VideoPlatform | None = None
    duration: int | None = None
    article_id: int | None = None
    project_id: int | None = None


class VideoRead(VideoBase):
    id: int
