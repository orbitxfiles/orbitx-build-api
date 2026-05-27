"""enable RLS on all public tables (Supabase Security Advisor)

Revision ID: a1b2c3d4e5f6
Revises: 439201b1719a
Create Date: 2026-05-27

OrbitX uses FastAPI + direct Postgres (not Supabase PostgREST).
Enabling RLS with no permissive policies blocks anon/authenticated API access
while the postgres pooler user (table owner) used by FastAPI still works.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "439201b1719a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# All OrbitX tables exposed in public schema
TABLES = [
    "alembic_version",
    "users",
    "themes",
    "categories",
    "projects",
    "project_features",
    "project_tech_stack",
    "project_architecture_nodes",
    "articles",
    "article_sections",
    "videos",
    "resources",
    "comments",
    "newsletter_subscribers",
]


def _enable_rls(table: str) -> None:
    op.execute(f'ALTER TABLE public."{table}" ENABLE ROW LEVEL SECURITY')


def _disable_rls(table: str) -> None:
    op.execute(f'ALTER TABLE public."{table}" DISABLE ROW LEVEL SECURITY')


def upgrade() -> None:
    for table in TABLES:
        _enable_rls(table)


def downgrade() -> None:
    for table in reversed(TABLES):
        _disable_rls(table)
