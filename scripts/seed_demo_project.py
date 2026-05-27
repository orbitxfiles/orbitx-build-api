"""Seed the featured OrbitX Voice Pipeline demo project (large architecture diagram).

Run from api/ with venv active:
  python scripts/seed_demo_project.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

API_BASE = os.environ.get("ORBITX_API_BASE", "http://localhost:8000/api/v1").rstrip("/")

# Large diagram — subgraphs + many nodes/edges to stress-test DiagramRenderer.
BIG_ARCHITECTURE_MERMAID = """graph TD
  subgraph Client Layer
    Browser[Web Browser UI]
    Mic[Microphone PCM 16kHz]
    Speaker[Speaker Output]
    Viz[Live Metrics Panel]
  end

  subgraph Edge and Gateway
    CDN[Cloudflare CDN]
    LB[Load Balancer]
    GW[WebSocket Gateway]
    Auth[JWT Auth Middleware]
  end

  subgraph Streaming Pipeline
    STT[Deepgram Nova-3 STT]
    VAD[Voice Activity Detection]
    LLM[Gemini 2.0 Flash]
    TTS[ElevenLabs Turbo TTS]
    Buf[Audio Buffer Manager]
  end

  subgraph Data and Observability
    PG[(PostgreSQL)]
    Redis[(Redis Session Cache)]
    OTEL[OpenTelemetry Collector]
    Grafana[Grafana Dashboards]
    S3[(S3 Build Artifacts)]
  end

  subgraph Async Workers
    Q[Task Queue]
    W1[Transcript Worker]
    W2[Embedding Worker]
    W3[Analytics Worker]
  end

  Browser --> CDN
  Mic --> GW
  CDN --> LB
  LB --> GW
  GW --> Auth
  Auth --> STT
  STT --> VAD
  VAD --> LLM
  LLM --> TTS
  TTS --> Buf
  Buf --> Speaker
  GW --> Viz
  GW --> Redis
  STT --> PG
  LLM --> PG
  GW --> OTEL
  OTEL --> Grafana
  LLM --> Q
  Q --> W1
  Q --> W2
  Q --> W3
  W1 --> PG
  W2 --> PG
  W3 --> S3
  Viz --> Grafana"""

DEMO_PROJECT = {
    "title": "OrbitX Voice Pipeline",
    "slug": "orbitx-voice-pipeline",
    "tagline": "Real-time voice: STT → LLM → TTS with a huge interactive architecture map for testing.",
    "problem_statement": "Most voice demos hide latency behind buffering or pre-recorded audio. We wanted a transparent pipeline you can inspect, measure, and ship—without pretending streaming is solved.",
    "architecture_overview": "Pan and zoom the diagram below — it is intentionally large (client, edge, streaming, data, workers) so you can confirm layout, edges, and animations are working.",
    "architecture_mermaid": BIG_ARCHITECTURE_MERMAID,
    "lessons_learned": [
        {
            "title": "Measure every hop",
            "body": "Voice UX breaks when round-trip exceeds ~800ms. Per-stage timers matter more than aggregate averages.",
        },
        {
            "title": "Version your prompts",
            "body": "Treat prompts like code: version, diff, and regression-test against a golden utterance set.",
        },
    ],
    "tech_stack": [
        "Next.js",
        "FastAPI",
        "PostgreSQL",
        "Redis",
        "Deepgram",
        "Gemini",
        "ElevenLabs",
        "WebSockets",
        "OpenTelemetry",
    ],
    "core_features": [
        {
            "title": "Streaming STT",
            "description": "Partial transcripts with stable finalization for barge-in.",
        },
        {
            "title": "Token streaming LLM",
            "description": "Low-latency first token; chunked downstream to TTS.",
        },
        {
            "title": "Observable pipeline",
            "description": "Stage timings and errors surfaced in the UI and Grafana.",
        },
        {
            "title": "Interactive architecture",
            "description": "Large Mermaid map — pan, zoom, hover nodes, animated flow dots.",
        },
    ],
    "roadmap": [
        {"milestone": "Core WebSocket + STT path", "status": "done", "date": "Q1 2026"},
        {"milestone": "Production hardening + metrics", "status": "in_progress", "date": "May 2026"},
        {"milestone": "Public beta launch", "status": "planned", "date": "Q3 2026"},
    ],
    "thumbnail": None,
    "banner_image": None,
    "walkthrough_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "walkthrough_duration": "12 min",
    "github_url": "https://github.com/orbitx/voice-pipeline",
    "demo_url": "https://demo.orbitx.dev/voice",
    "build_logs_url": "https://orbitx.dev/what-broke",
    "accent_color": "#1a7a5e",
    "icon_label": "OV",
    "status": "building",
    "is_featured": True,
    "visibility": "public",
    "featured_article_ids": [],
}


def api_request(method: str, path: str, payload: dict | None = None, token: str | None = None):
    url = f"{API_BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, method=method, headers=headers, data=data)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} {method} {path}: {raw}") from e


def ensure_admin_token(email: str, password: str) -> str:
    try:
        res = api_request("POST", "/auth/login", payload={"email": email, "password": password})
        return res["access_token"]
    except RuntimeError:
        api_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cmd = [
            sys.executable,
            os.path.join(api_dir, "scripts", "create_admin.py"),
            "Demo Admin",
            email,
            password,
        ]
        env = os.environ.copy()
        env["PYTHONPATH"] = api_dir
        subprocess.run(cmd, cwd=api_dir, env=env, check=False)
        res = api_request("POST", "/auth/login", payload={"email": email, "password": password})
        return res["access_token"]


def main() -> int:
    themes = api_request("GET", "/themes")
    if not themes:
        print("No themes found. Run: python scripts/seed_themes.py")
        return 1

    payload = {**DEMO_PROJECT, "theme_id": themes[0]["id"]}
    slug = payload["slug"]

    ts = int(time.time())
    email = os.environ.get("ORBITX_DEMO_ADMIN_EMAIL", f"demo-admin-{ts}@orbitx.dev")
    password = os.environ.get("ORBITX_DEMO_ADMIN_PASSWORD", "demo-password")
    token = ensure_admin_token(email, password)

    try:
        api_request("PUT", f"/projects/{slug}", payload=payload, token=token)
        action = "updated"
    except RuntimeError as e:
        if "404" not in str(e):
            raise
        api_request("POST", "/projects", payload=payload, token=token)
        action = "created"

    print(f"Demo project {action}: {slug}")
    print(f"View: http://localhost:3000/projects/{slug}")
    print(f"Edit: http://localhost:3000/admin/projects/{slug}/edit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
