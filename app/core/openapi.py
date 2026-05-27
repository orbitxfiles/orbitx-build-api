"""OpenAPI / Swagger configuration for /docs."""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

API_DESCRIPTION = """
## OrbitX API

Content + system engine for the OrbitX platform (projects, articles, themes, CMS).

### Authentication (JWT)

This API uses **Bearer JWT tokens**, not Supabase anon keys for data access.

1. Create an admin user: `python scripts/create_admin.py`
2. **Login:** `POST /api/v1/auth/login` with email + password
3. Copy `access_token` from the response
4. Click **Authorize** (top right) → paste: `Bearer <access_token>` or just the token
5. Call protected routes (create/update/delete)

| Role | Access |
|------|--------|
| `admin` | Full CRUD, delete, themes |
| `editor` | Create/update content |
| `contributor` | Create/update own content |

**Refresh:** `POST /api/v1/auth/refresh` with `refresh_token` when access token expires.

### Environment keys

See **[GET /docs/keys](/docs/keys)** for required `.env` variables (no secret values returned).

### Supabase

- Use **Session pooler** `DATABASE_URL` in `.env` (IPv4-friendly on Windows)
- Do **not** expose Supabase `service_role` or DB password in the frontend
- Frontend should call this API via `NEXT_PUBLIC_API_URL`, not Supabase REST for CMS tables
"""

OPENAPI_TAGS = [
    {
        "name": "auth",
        "description": "Login, refresh, logout, current user. Start here to get a JWT.",
    },
    {
        "name": "documentation",
        "description": "API keys and environment variable reference (no secrets).",
    },
    {
        "name": "themes",
        "description": "Dynamic design systems per section/project. Admin write.",
    },
    {
        "name": "projects",
        "description": "First-class project entities with features, stack, architecture.",
    },
    {
        "name": "articles",
        "description": "Articles, sections, markdown + structured blocks.",
    },
    {
        "name": "categories",
        "description": "Content categories linked to themes.",
    },
    {
        "name": "videos",
        "description": "Embedded videos for articles/projects.",
    },
    {
        "name": "resources",
        "description": "Downloadable assets (PDFs, templates, etc.).",
    },
    {
        "name": "comments",
        "description": "Public comments on articles.",
    },
    {
        "name": "search",
        "description": "Full-text search across articles, projects, resources.",
    },
    {
        "name": "newsletter",
        "description": "Newsletter subscriptions.",
    },
]


def setup_openapi(app: FastAPI) -> None:
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=API_DESCRIPTION,
            routes=app.routes,
            tags=OPENAPI_TAGS,
        )

        schema.setdefault("components", {}).setdefault("securitySchemes", {})
        schema["components"]["securitySchemes"]["BearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": (
                "JWT **access_token** from `POST /api/v1/auth/login`. "
                "Paste the token only, or prefix with `Bearer `."
            ),
        }

        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi
