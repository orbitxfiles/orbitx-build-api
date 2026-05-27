from datetime import datetime

from pydantic import EmailStr

from app.schemas.common import OrbitXSchema


class NewsletterSubscribe(OrbitXSchema):
    email: EmailStr
    source: str | None = None


class NewsletterSubscriberRead(OrbitXSchema):
    id: int
    email: str
    source: str | None
    subscribed_at: datetime
