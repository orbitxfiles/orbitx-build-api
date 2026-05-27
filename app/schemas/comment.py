from datetime import datetime

from pydantic import EmailStr

from app.schemas.common import OrbitXSchema


class CommentCreate(OrbitXSchema):
    user_name: str
    user_email: EmailStr
    content: str


class CommentRead(OrbitXSchema):
    id: int
    article_id: int
    user_name: str
    user_email: str
    content: str
    created_at: datetime
