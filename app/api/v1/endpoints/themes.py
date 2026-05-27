from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import AdminUser, DbSession
from app.models.theme import Theme
from app.schemas.common import MessageResponse
from app.schemas.theme import ThemeCreate, ThemeRead, ThemeUpdate
from app.utils import apply_updates

router = APIRouter(prefix="/themes", tags=["themes"])


@router.get("", response_model=list[ThemeRead])
def list_themes(db: DbSession):
    return list(db.scalars(select(Theme).order_by(Theme.name)).all())


@router.get("/{theme_id}", response_model=ThemeRead)
def get_theme(theme_id: int, db: DbSession):
    theme = db.get(Theme, theme_id)
    if theme is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Theme not found")
    return theme


@router.post("", response_model=ThemeRead, status_code=status.HTTP_201_CREATED)
def create_theme(payload: ThemeCreate, db: DbSession, _: AdminUser):
    theme = Theme(**payload.model_dump())
    db.add(theme)
    db.commit()
    db.refresh(theme)
    return theme


@router.patch("/{theme_id}", response_model=ThemeRead)
def update_theme(theme_id: int, payload: ThemeUpdate, db: DbSession, _: AdminUser):
    theme = db.get(Theme, theme_id)
    if theme is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Theme not found")
    apply_updates(theme, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(theme)
    return theme


@router.delete("/{theme_id}", response_model=MessageResponse)
def delete_theme(theme_id: int, db: DbSession, _: AdminUser):
    theme = db.get(Theme, theme_id)
    if theme is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Theme not found")
    db.delete(theme)
    db.commit()
    return MessageResponse(message="Theme deleted")
