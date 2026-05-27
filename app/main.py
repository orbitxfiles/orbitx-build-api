from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.docs_keys import router as docs_keys_router
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.openapi import setup_openapi

settings = get_settings()

app = FastAPI(
    title="OrbitX API",
    description="Content + system engine for OrbitX. See /docs/keys for environment variables.",
    version="1.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True,
        "docExpansion": "list",
    },
)

setup_openapi(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(docs_keys_router)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["documentation"])
def health_check():
    return {"status": "ok", "service": "orbitx-api", "docs": "/docs", "keys": "/docs/keys"}
