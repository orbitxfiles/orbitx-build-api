"""Seed default OrbitX section themes."""

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.theme import Theme

import app.models  # noqa: F401

DEFAULT_THEMES = [
    {
        "name": "OrbitX Main",
        "slug": "orbitx-main",
        "primary_color": "#22c55e",
        "secondary_color": "#16a34a",
        "accent_color": "#4ade80",
        "background_color": "#0a0f0a",
        "is_default": True,
    },
    {
        "name": "What Broke",
        "slug": "what-broke",
        "primary_color": "#ef4444",
        "secondary_color": "#dc2626",
        "accent_color": "#f87171",
        "background_color": "#1a0a0a",
    },
    {
        "name": "Learn",
        "slug": "learn",
        "primary_color": "#a855f7",
        "secondary_color": "#9333ea",
        "accent_color": "#c084fc",
        "background_color": "#0f0a1a",
    },
    {
        "name": "Hackathons",
        "slug": "hackathons",
        "primary_color": "#f97316",
        "secondary_color": "#ea580c",
        "accent_color": "#fb923c",
        "background_color": "#1a1008",
    },
    {
        "name": "Updates",
        "slug": "updates",
        "primary_color": "#6b7280",
        "secondary_color": "#4b5563",
        "accent_color": "#9ca3af",
        "background_color": "#111827",
    },
]


def main() -> None:
    db = SessionLocal()
    try:
        for data in DEFAULT_THEMES:
            exists = db.scalar(select(Theme).where(Theme.slug == data["slug"]))
            if exists:
                continue
            db.add(Theme(**data))
        db.commit()
        print("Default themes seeded.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
