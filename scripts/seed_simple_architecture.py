"""Push a minimal architecture diagram to the demo project via API.

Run from api/ with venv active:
  python scripts/seed_simple_architecture.py
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
SLUG = "orbitx-voice-pipeline"

# Minimal LR pipeline — easy to read, good for layout/icon smoke test.
SIMPLE_MERMAID = """graph LR
  Client[Web Client]
  Gateway[API Gateway]
  LLM[Gemini LLM]
  DB[(PostgreSQL)]
  Client --> Gateway
  Gateway --> LLM
  LLM --> DB
  Gateway --> DB"""

PATCH_BODY = {
    "tagline": "Simple 4-node pipeline — quick diagram check.",
    "architecture_overview": "A minimal left-to-right flow: client → gateway → LLM → database.",
    "architecture_mermaid": SIMPLE_MERMAID,
    "tech_stack": ["Next.js", "FastAPI", "PostgreSQL", "Gemini"],
    "core_features": [
        {"title": "Single API path", "description": "One gateway handles all requests."},
        {"title": "LLM step", "description": "Gemini generates the response."},
    ],
    "lessons_learned": [
        {
            "title": "Start simple",
            "body": "Four nodes are enough to validate layout, icons, and edge routing.",
        }
    ],
    "roadmap": [
        {"milestone": "Simple diagram", "status": "done", "date": "Today"},
        {"milestone": "Add observability", "status": "planned", "date": "Next"},
    ],
}


def api_request(method: str, path: str, payload: dict | None = None, token: str | None = None):
    url = f"{API_BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
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
        env = os.environ.copy()
        env["PYTHONPATH"] = api_dir
        subprocess.run(
            [sys.executable, os.path.join(api_dir, "scripts", "create_admin.py"), "Demo Admin", email, password],
            cwd=api_dir,
            env=env,
            check=False,
        )
        res = api_request("POST", "/auth/login", payload={"email": email, "password": password})
        return res["access_token"]


def main() -> int:
    ts = int(time.time())
    email = os.environ.get("ORBITX_DEMO_ADMIN_EMAIL", f"simple-demo-{ts}@orbitx.dev")
    password = os.environ.get("ORBITX_DEMO_ADMIN_PASSWORD", "demo-password")
    token = ensure_admin_token(email, password)

    result = api_request("PATCH", f"/projects/{SLUG}", payload=PATCH_BODY, token=token)
    print("Updated project:", result.get("slug", SLUG))
    print("View: http://localhost:3000/projects/" + SLUG)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
