import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request


API_BASE = os.environ.get("ORBITX_API_BASE", "http://localhost:8000/api/v1").rstrip("/")


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
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8")
            if not raw:
                return None
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} {method} {path}: {raw}") from e


def ensure_admin_token(email: str, password: str) -> str:
    try:
        res = api_request("POST", "/auth/login", payload={"email": email, "password": password})
        return res["access_token"]
    except RuntimeError:
        # Create admin user if it doesn't exist yet
        # Run from repo root.
        api_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cmd = [
            sys.executable,
            os.path.join(api_dir, "scripts", "create_admin.py"),
            "Smoke Admin",
            email,
            password,
        ]
        env = os.environ.copy()
        env["PYTHONPATH"] = api_dir
        subprocess.run(cmd, cwd=api_dir, env=env, check=False)
        res = api_request("POST", "/auth/login", payload={"email": email, "password": password})
        return res["access_token"]


def main() -> int:
    ts = int(time.time())
    email = os.environ.get("ORBITX_SMOKE_ADMIN_EMAIL")
    if not email:
        email = f"smoke-admin-{ts}@orbitx.dev"
    password = os.environ.get("ORBITX_SMOKE_ADMIN_PASSWORD", "smoke-password")

    # 1) Basic GETs
    projects = api_request("GET", "/projects?page=1&page_size=20")
    items = projects.get("items") or []
    if items:
        slug = items[0]["slug"]
        _ = api_request("GET", f"/projects/{slug}")

    themes = api_request("GET", "/themes")
    if not themes:
        raise RuntimeError("No themes found; run `python scripts/seed_themes.py` first.")
    theme_id = themes[0]["id"]

    # 2) POST new project (admin/editor)
    token = ensure_admin_token(email, password)

    slug_new = f"smoke-project-{ts}"
    payload_create = {
        "title": f"Smoke Project {ts}",
        "slug": slug_new,
        "tagline": "A smoke-test project for the new OrbitX schema.",
        "problem_statement": "We need a quick end-to-end check of GET/POST/PATCH for projects.",
        "architecture_overview": "graphical overview lives in `architecture_mermaid`; this is a plain paragraph.",
        "architecture_mermaid": "graph TD\n  A[Client] --> B[Server]\n  B --> C[Workers]",
        "lessons_learned": [{"title": "Fast validation", "body": "Use strict schemas to catch issues early."}],
        "tech_stack": ["FastAPI", "PostgreSQL", "React"],
        "core_features": [{"title": "Schema-driven API", "description": "Pydantic ensures stable shapes."}],
        "roadmap": [{"milestone": "Ship smoke tests", "status": "planned", "date": "Q2 2026"}],
        "thumbnail": None,
        "banner_image": None,
        "walkthrough_url": None,
        "walkthrough_duration": None,
        "github_url": None,
        "demo_url": None,
        "build_logs_url": None,
        "accent_color": "#1a7a5e",
        "icon_label": "SP",
        "status": "planning",
        "is_featured": False,
        "visibility": "public",
        "theme_id": theme_id,
        "featured_article_ids": [],
    }
    created = api_request("POST", "/projects", payload=payload_create, token=token)
    created_slug = created["slug"]

    # 3) PATCH project (admin/editor)
    payload_patch = {"tagline": "Updated tagline after PATCH smoke test."}
    patched = api_request("PATCH", f"/projects/{created_slug}", payload=payload_patch, token=token)
    assert patched["tagline"] == payload_patch["tagline"]

    print("Smoke test OK:", {"created_slug": created_slug})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

