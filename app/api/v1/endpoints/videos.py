from fastapi import APIRouter, HTTPException, status

from app.core.deps import DbSession, EditorUser
from app.models.video import Video
from app.schemas.common import MessageResponse
from app.schemas.video import VideoCreate, VideoRead, VideoUpdate
from app.utils import apply_updates

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("", response_model=VideoRead, status_code=status.HTTP_201_CREATED)
def create_video(payload: VideoCreate, db: DbSession, _: EditorUser):
    video = Video(**payload.model_dump())
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


@router.patch("/{video_id}", response_model=VideoRead)
def update_video(video_id: int, payload: VideoUpdate, db: DbSession, _: EditorUser):
    video = db.get(Video, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    apply_updates(video, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(video)
    return video


@router.delete("/{video_id}", response_model=MessageResponse)
def delete_video(video_id: int, db: DbSession, _: EditorUser):
    video = db.get(Video, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    db.delete(video)
    db.commit()
    return MessageResponse(message="Video deleted")
