from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import DbSession
from app.models.newsletter import NewsletterSubscriber
from app.schemas.common import MessageResponse
from app.schemas.newsletter import NewsletterSubscribe, NewsletterSubscriberRead

router = APIRouter(prefix="/newsletter", tags=["newsletter"])


@router.post("/subscribe", response_model=NewsletterSubscriberRead, status_code=status.HTTP_201_CREATED)
def subscribe(payload: NewsletterSubscribe, db: DbSession):
    existing = db.scalar(
        select(NewsletterSubscriber).where(NewsletterSubscriber.email == payload.email)
    )
    if existing:
        raise HTTPException(status_code=400, detail="Email already subscribed")
    subscriber = NewsletterSubscriber(**payload.model_dump())
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)
    return subscriber
