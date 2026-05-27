"""Seed three OrbitX projects with distinct accent colors for theme testing.

Run from api/ with venv active:
  $env:PYTHONPATH = (Get-Location).Path
  python scripts/seed_three_projects.py
"""

from __future__ import annotations

from sqlalchemy import select

import app.models  # noqa: F401
from app.core.database import SessionLocal
from app.models.project import Project, ProjectStatus, ProjectVisibility

MERMAID_LR = """graph LR
  Client[Client]
  API[API Gateway]
  Core[Core Service]
  DB[(Database)]
  Client --> API --> Core --> DB"""

PROJECTS = [
    {
        "title": "OrbitX Voice Pipeline",
        "slug": "orbitx-voice-pipeline",
        "tagline": "Real-time voice: STT → LLM → TTS with a live architecture map.",
        "problem_statement": "Voice demos hide latency. We built a transparent streaming pipeline you can measure and ship.",
        "architecture_overview": "Left-to-right streaming path with observability on every hop.",
        "architecture_mermaid": MERMAID_LR.replace("Core Service", "Gemini LLM").replace("Core", "LLM"),
        "accent_color": "#1a7a5e",
        "icon_label": "OV",
        "tech_stack": ["Next.js", "FastAPI", "Deepgram", "Gemini", "ElevenLabs"],
        "core_features": [
            {"title": "Streaming STT", "description": "Partial transcripts with barge-in."},
            {"title": "Token streaming", "description": "Low-latency first token to TTS."},
        ],
        "roadmap": [
            {"milestone": "WebSocket path", "status": "done", "date": "Q1 2026"},
            {"milestone": "Public beta", "status": "in_progress", "date": "Q3 2026"},
        ],
        "lessons_learned": [
            {"title": "Measure every hop", "body": "Per-stage timers beat aggregate latency averages."},
        ],
        "is_featured": True,
    },
    {
        "title": "OrbitX RAG Engine",
        "slug": "orbitx-rag-engine",
        "tagline": "Production retrieval with hybrid search, reranking, and eval gates.",
        "problem_statement": "Most RAG stacks fail silently when retrieval quality drops. We treat recall as a product metric.",
        "architecture_overview": "Embed, retrieve, rerank, then generate — with score thresholds and golden evals.",
        "architecture_mermaid": MERMAID_LR.replace("Core Service", "RAG Core").replace("Core", "RAG"),
        "accent_color": "#6b4fa0",
        "icon_label": "RG",
        "tech_stack": ["Python", "pgvector", "LangChain", "Gemini", "OpenTelemetry"],
        "core_features": [
            {"title": "Hybrid search", "description": "BM25 + vector fusion with metadata filters."},
            {"title": "Eval harness", "description": "Golden questions with expected chunk IDs."},
        ],
        "roadmap": [
            {"milestone": "Indexer v1", "status": "done", "date": "Apr 2026"},
            {"milestone": "Reranker v2", "status": "in_progress", "date": "Jun 2026"},
        ],
        "lessons_learned": [
            {"title": "Threshold before generate", "body": "Low-similarity chunks cause confident hallucinations."},
        ],
        "is_featured": True,
    },
    {
        "title": "OrbitX Agent Hub",
        "slug": "orbitx-agent-hub",
        "tagline": "Multi-agent orchestration with tool validation and traced execution.",
        "problem_statement": "Single-shot prompts do not survive production tool chains. Agents need structure, limits, and observability.",
        "architecture_overview": "Supervisor routes to specialist agents with shared memory and strict tool schemas.",
        "architecture_mermaid": """graph LR
  User[User] --> Sup[Supervisor]
  Sup --> Res[Researcher]
  Sup --> Cod[Coder]
  Sup --> Mem[(Memory)]
  Res --> Mem
  Cod --> Mem""",
        "accent_color": "#b45309",
        "icon_label": "AH",
        "tech_stack": ["LangGraph", "FastAPI", "Pydantic", "Redis", "PostgreSQL"],
        "core_features": [
            {"title": "Tool schemas", "description": "Pydantic-validated args on every call."},
            {"title": "Trace per step", "description": "OpenTelemetry spans for plan and act."},
        ],
        "roadmap": [
            {"milestone": "Supervisor MVP", "status": "done", "date": "May 2026"},
            {"milestone": "Human approval path", "status": "planned", "date": "Jul 2026"},
        ],
        "lessons_learned": [
            {"title": "Read-only default", "body": "Agents start without write tools until escalated."},
        ],
        "is_featured": True,
    },
]


def upsert_project(db, data: dict) -> str:
    slug = data["slug"]
    existing = db.scalar(select(Project).where(Project.slug == slug))
    fields = {
        **data,
        "status": ProjectStatus.BUILDING,
        "visibility": ProjectVisibility.PUBLIC,
    }
    if existing:
        for k, v in fields.items():
            setattr(existing, k, v)
        return "updated"
    db.add(Project(**fields))
    return "created"


def main() -> None:
    db = SessionLocal()
    try:
        results = []
        for p in PROJECTS:
            results.append(f"{p['slug']}: {upsert_project(db, p)}")
        db.commit()
        print("Three projects seeded:")
        for r in results:
            print(f"  - {r}")
        print("\nView:")
        for p in PROJECTS:
            print(f"  http://localhost:3000/projects/{p['slug']}  ({p['accent_color']})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
