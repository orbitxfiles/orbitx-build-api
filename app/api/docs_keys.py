"""Public reference for API / environment keys (no secret values)."""

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["documentation"])

ENV_KEYS = [
    {
        "name": "DATABASE_URL",
        "required": True,
        "secret": True,
        "description": "PostgreSQL connection string (Supabase Session pooler recommended).",
        "example": "postgresql://postgres.[project-ref]:****@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres?sslmode=require",
    },
    {
        "name": "SECRET_KEY",
        "required": True,
        "secret": True,
        "description": "Signing key for JWT access/refresh tokens. Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\"",
        "example": "(random 32+ char string)",
    },
    {
        "name": "ALGORITHM",
        "required": False,
        "secret": False,
        "default": "HS256",
        "description": "JWT signing algorithm.",
    },
    {
        "name": "ACCESS_TOKEN_EXPIRE_MINUTES",
        "required": False,
        "secret": False,
        "default": "60",
        "description": "Access token lifetime in minutes.",
    },
    {
        "name": "REFRESH_TOKEN_EXPIRE_DAYS",
        "required": False,
        "secret": False,
        "default": "7",
        "description": "Refresh token lifetime in days.",
    },
    {
        "name": "CORS_ORIGINS",
        "required": False,
        "secret": False,
        "default": "http://localhost:3000",
        "description": "Comma-separated allowed origins for the Next.js frontend.",
    },
    {
        "name": "API_V1_PREFIX",
        "required": False,
        "secret": False,
        "default": "/api/v1",
        "description": "URL prefix for all versioned routes.",
    },
    {
        "name": "ENVIRONMENT",
        "required": False,
        "secret": False,
        "default": "development",
        "description": "Runtime environment label.",
    },
]

FRONTEND_KEYS = [
    {
        "name": "NEXT_PUBLIC_API_URL",
        "where": "orbitx-builds/web/.env",
        "secret": False,
        "description": "Base URL for this FastAPI server (no trailing slash).",
        "example": "http://localhost:8000",
    },
]

SUPABASE_KEYS = [
    {
        "name": "DATABASE_URL (pooler)",
        "where": "api/.env",
        "use": "FastAPI + Alembic migrations",
        "never_in_frontend": True,
        "note": "Session pooler URI from Supabase Dashboard → Database → Connection string.",
    },
    {
        "name": "anon key",
        "where": "Supabase Dashboard → API",
        "use": "Only if using Supabase Auth/Storage directly",
        "never_in_frontend": False,
        "note": "Do NOT use for OrbitX CMS table CRUD — use this API instead. RLS blocks direct table access.",
    },
    {
        "name": "service_role key",
        "where": "Supabase Dashboard → API",
        "use": "Server-side admin scripts only",
        "never_in_frontend": True,
        "note": "Bypasses RLS. Never ship to browser or Next.js client bundle.",
    },
]


@router.get(
    "/docs/keys",
    summary="Environment & API keys reference",
    description="Lists required `.env` variables and auth flow. Does not return secret values.",
)
def get_api_keys_reference():
    settings = get_settings()
    return {
        "service": "orbitx-api",
        "docs_ui": "/docs",
        "openapi_json": "/openapi.json",
        "authentication": {
            "type": "JWT Bearer",
            "header": "Authorization: Bearer <access_token>",
            "obtain_token": "POST /api/v1/auth/login",
            "refresh": "POST /api/v1/auth/refresh",
            "swagger_authorize": "Click Authorize in /docs and paste your access_token",
        },
        "configured": {
            "api_v1_prefix": settings.API_V1_PREFIX,
            "cors_origins": settings.cors_origin_list,
            "environment": settings.ENVIRONMENT,
            "database_configured": bool(settings.DATABASE_URL),
            "secret_key_configured": bool(settings.SECRET_KEY),
        },
        "backend_env": ENV_KEYS,
        "frontend_env": FRONTEND_KEYS,
        "supabase": SUPABASE_KEYS,
    }
