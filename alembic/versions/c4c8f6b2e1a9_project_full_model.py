"""project full model columns

Revision ID: c4c8f6b2e1a9
Revises: a1b2c3d4e5f6
Create Date: 2026-05-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4c8f6b2e1a9"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = getattr(bind.dialect, "name", "") == "postgresql"

    json_col_type = sa.JSON
    server_json_default = sa.text("'[]'")
    if is_postgres:
        json_col_type = sa.dialects.postgresql.JSONB
        server_json_default = sa.text("'[]'::jsonb")

    # --- Enums: status and visibility (legacy values mapped) ---
    if is_postgres:
        op.execute(
            "CREATE TYPE project_status_new AS ENUM ('planning','building','launched','archived')"
        )
        op.execute(
            """
            ALTER TABLE projects
            ALTER COLUMN status TYPE project_status_new
            USING (
              CASE
                WHEN status::text = 'beta' THEN 'building'
                ELSE status::text
              END
            )::project_status_new
            """
        )
        op.execute("ALTER TYPE project_status RENAME TO project_status_old")
        op.execute("ALTER TYPE project_status_new RENAME TO project_status")
        op.execute("DROP TYPE project_status_old")

        op.execute(
            "CREATE TYPE project_visibility_new AS ENUM ('public','unlisted','private')"
        )
        op.execute(
            """
            ALTER TABLE projects
            ALTER COLUMN visibility TYPE project_visibility_new
            USING (
              CASE
                WHEN visibility::text = 'draft' THEN 'unlisted'
                ELSE visibility::text
              END
            )::project_visibility_new
            """
        )
        op.execute("ALTER TYPE project_visibility RENAME TO project_visibility_old")
        op.execute("ALTER TYPE project_visibility_new RENAME TO project_visibility")
        op.execute("DROP TYPE project_visibility_old")

    # --- Required plain text columns (backfill + NOT NULL) ---
    op.execute("UPDATE projects SET problem_statement = COALESCE(problem_statement, '') WHERE problem_statement IS NULL")
    op.execute(
        "UPDATE projects SET architecture_overview = COALESCE(architecture_overview, '') WHERE architecture_overview IS NULL"
    )

    # --- New columns ---
    op.add_column(
        "projects",
        sa.Column(
            "tagline",
            sa.String(length=120),
            nullable=False,
            server_default="",
        ),
    )
    op.execute(
        """
        UPDATE projects
        SET tagline = COALESCE(tagline, short_description, title)
        WHERE tagline = ''
        """
    )

    op.alter_column("projects", "problem_statement", nullable=False)
    op.alter_column("projects", "architecture_overview", nullable=False)

    op.add_column(
        "projects",
        sa.Column("architecture_mermaid", sa.Text(), nullable=True),
    )
    op.add_column(
        "projects",
        sa.Column(
            "lessons_learned",
            json_col_type,
            nullable=True,
            server_default=server_json_default,
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "tech_stack",
            json_col_type,
            nullable=True,
            server_default=server_json_default,
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "core_features",
            json_col_type,
            nullable=True,
            server_default=server_json_default,
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "roadmap",
            json_col_type,
            nullable=True,
            server_default=server_json_default,
        ),
    )

    op.add_column(
        "projects",
        sa.Column("walkthrough_url", sa.String(length=512), nullable=True),
    )
    op.add_column(
        "projects",
        sa.Column("walkthrough_duration", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "projects",
        sa.Column("build_logs_url", sa.String(length=512), nullable=True),
    )

    op.add_column(
        "projects",
        sa.Column(
            "accent_color",
            sa.String(length=7),
            nullable=True,
            server_default="#1a7a5e",
        ),
    )
    op.add_column(
        "projects",
        sa.Column("icon_label", sa.String(length=2), nullable=True),
    )

    # Replaces featured_article_id
    op.add_column(
        "projects",
        sa.Column(
            "featured_article_ids",
            json_col_type,
            nullable=True,
            server_default=server_json_default,
        ),
    )
    op.execute(
        """
        UPDATE projects
        SET featured_article_ids = CASE
          WHEN featured_article_id IS NULL THEN '[]'
          ELSE json_build_array(featured_article_id)
        END
        """
    )


def downgrade() -> None:
    # Non-destructive approach: for downgrade, keep compatibility by only dropping new columns.
    op.drop_column("projects", "featured_article_ids")
    op.drop_column("projects", "icon_label")
    op.drop_column("projects", "accent_color")
    op.drop_column("projects", "build_logs_url")
    op.drop_column("projects", "walkthrough_duration")
    op.drop_column("projects", "walkthrough_url")
    op.drop_column("projects", "roadmap")
    op.drop_column("projects", "core_features")
    op.drop_column("projects", "tech_stack")
    op.drop_column("projects", "lessons_learned")
    op.drop_column("projects", "architecture_mermaid")
    op.drop_column("projects", "tagline")

