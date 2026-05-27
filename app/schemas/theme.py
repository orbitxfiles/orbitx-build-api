from datetime import datetime

from pydantic import Field

from app.schemas.common import OrbitXSchema


class ThemeBase(OrbitXSchema):
    name: str
    slug: str
    primary_color: str = "#22c55e"
    secondary_color: str = "#16a34a"
    accent_color: str = "#4ade80"
    background_color: str = "#0a0f0a"
    text_color: str = "#e5e7eb"
    strong_text_color: str = "#ffffff"
    muted_text_color: str = "#9ca3af"
    border_color: str = "#1f2937"
    heading_font: str = "Inter"
    body_font: str = "Inter"
    serif_font: str | None = None
    button_radius: str = "0.5rem"
    card_radius: str = "0.75rem"
    shadow_style: str | None = None
    is_default: bool = False


class ThemeCreate(ThemeBase):
    pass


class ThemeUpdate(OrbitXSchema):
    name: str | None = None
    slug: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    accent_color: str | None = None
    background_color: str | None = None
    text_color: str | None = None
    strong_text_color: str | None = None
    muted_text_color: str | None = None
    border_color: str | None = None
    heading_font: str | None = None
    body_font: str | None = None
    serif_font: str | None = None
    button_radius: str | None = None
    card_radius: str | None = None
    shadow_style: str | None = None
    is_default: bool | None = None


class ThemeRead(ThemeBase):
    id: int
    created_at: datetime
