"""Seed OrbitX Academy categories and sample articles for /learn testing.

Run from api/ with venv active:
  python scripts/seed_academy_articles.py
"""

from __future__ import annotations

from sqlalchemy import select

import app.models  # noqa: F401
from app.core.database import SessionLocal
from app.models.article import Article, ContentVisibility
from app.models.category import Category
from app.models.project import Project
from app.models.theme import Theme
from app.models.user import User

CATEGORIES = [
    {"name": "RAG", "slug": "rag"},
    {"name": "Agents", "slug": "agents"},
    {"name": "LangGraph", "slug": "langgraph"},
    {"name": "Vector DBs", "slug": "vector-dbs"},
    {"name": "MCP", "slug": "mcp"},
    {"name": "Prompt Engineering", "slug": "prompt-engineering"},
    {"name": "Structured Outputs", "slug": "structured-outputs"},
]

RAG_PIPELINE_MD = """\
Retrieval-augmented generation is easy to prototype and hard to ship. This guide walks through the decisions we made while wiring RAG into a production voice pipeline — indexing, retrieval, and guardrails included.

## Why retrieval quality matters

Most RAG failures are not model failures. They are **retrieval failures**: wrong chunks, stale documents, or embeddings that do not align with how users actually ask questions.

### Embedding model choice

We started with a general-purpose embedding model and moved to a smaller, domain-tuned encoder once we measured recall@5 on our eval set. The lesson: pick the metric first, then the model.

### Chunk size tradeoffs

| Strategy | Pros | Cons |
| --- | --- | --- |
| Fixed 512 tokens | Simple, predictable | Splits tables and code awkwardly |
| Semantic splits | Better coherence | Higher indexing cost |
| Parent-child | Good for citations | More complex query path |

## Implementation walkthrough

A minimal retriever loop looks like this:

```python
from orbitx.rag import embed_query, search_chunks, build_context

def answer(question: str, top_k: int = 6) -> str:
    vector = embed_query(question)
    chunks = search_chunks(vector, top_k=top_k, min_score=0.72)
    context = build_context(chunks)
    return llm.complete(system=SYSTEM, user=f"{context}\\n\\nQ: {question}")
```

Use a **score threshold** early. Without it, low-similarity chunks pollute the context window and the model hallucinates confidently.

## Common failures we hit

> The worst bugs were silent: retrieval returned *something*, so the UI looked healthy while answers drifted from our docs.

- **Stale index** — deploy hooks must re-embed changed pages.
- **Duplicate chunks** — near-identical sections dominated top-k.
- **Over-long context** — more tokens ≠ better answers past ~3k tokens of evidence.

## Hardening checklist

1. Log `chunk_id`, score, and latency on every request.
2. Keep a golden set of 30 questions with expected source IDs.
3. Add a "no relevant docs" path when max score is below threshold.

## Next steps

Pair this pipeline with [structured tool outputs](/learn/structured-outputs-json-schema) when agents need to call internal APIs safely.
"""

AGENTS_MD = """\
## The agent loop

A useful agent is not a single prompt — it is a **loop**: observe state, plan, act, verify. We standardize that loop across products so debugging stays familiar.

### Planning vs. acting

Split planning from execution when tools have side effects. The planner proposes steps; the executor validates arguments before calling APIs.

## Tool design

```typescript
const searchDocs = tool({
  name: "search_docs",
  description: "Search internal markdown. Use for product questions only.",
  parameters: z.object({ query: z.string().min(3), limit: z.number().max(10).default(5) }),
  execute: async ({ query, limit }) => rag.search(query, limit),
});
```

**Rules we enforce:**

- One responsibility per tool
- Hard limits on `limit` and payload size
- Idempotent reads only in the default path

## Observability

Log every tool call with latency, status, and truncated input. When something breaks at 2 a.m., you will want a trace — not a screenshot of ChatGPT.

## When not to use agents

If the task is a fixed DAG, use LangGraph or plain code. Agents earn their cost when branches depend on intermediate results.
"""

LANGGRAPH_MD = """\
## Why graphs beat chains

Chains hide state. Graphs make state explicit — which matters when you need retries, human approval, or parallel branches.

## Core concepts

### Nodes

Each node is a pure function `(state) -> partial state`. Keep nodes small: retrieve, rank, draft, verify.

### Edges

Conditional edges encode business rules:

```python
def route_after_verify(state: AgentState) -> str:
    if state["confidence"] >= 0.85:
        return "publish"
    if state["attempts"] < 3:
        return "revise"
    return "escalate"
```

## Checkpointing

Persist checkpoints to Postgres so a deploy does not wipe in-flight workflows. We store `thread_id`, `node`, and a redacted snapshot.

## Testing

Run graph units with frozen state fixtures. Integration tests should cover at least one failure edge per conditional.
"""

VECTOR_MD = """\
## What actually matters

Vector databases differ less than marketing suggests. Prioritize **operational fit**: backups, filtering, hybrid search, and cost at your expected QPS.

## Evaluation matrix

### Recall under load

Benchmark with your real embedding model and chunk sizes — not the vendor's toy dataset.

### Metadata filters

Production queries almost always need `tenant_id`, `doc_type`, or `published_at` filters. Test those in the benchmark.

## Hybrid search

Combine BM25 + vectors when users type exact SKUs, error codes, or internal acronyms. Pure semantic search misses those.

## Migration notes

Re-embed everything when you change chunking strategy. Partial re-indexes create invisible quality cliffs.
"""

MCP_MD = """\
## What MCP gives you

Model Context Protocol servers expose tools and resources to clients in a standard shape — useful when you have more than one IDE or agent host.

## Minimal server

```python
from mcp.server import Server

app = Server("orbitx-docs")

@app.tool()
async def get_runbook(slug: str) -> str:
    return load_markdown(f"runbooks/{slug}.md")
```

## Security

- Bind to localhost in development
- Scope API keys per server, not shared global keys
- Audit tool invocations the same way you audit HTTP handlers

## Shipping checklist

Package with a pinned SDK version, document required env vars, and provide a `--check` command that validates credentials without side effects.
"""

PROMPT_MD = """\
## Reliability over cleverness

Prompts should be boring: explicit format, explicit refusal rules, and examples that match production traffic — not demo traffic.

## Template structure

1. Role and constraints (short)
2. Output schema or bullet format
3. Two positive examples + one edge case
4. What to do when information is missing

## Regression testing

Store prompts in git. When you change a prompt, run the golden eval set and compare pass rate — not vibes.

> A 2% eval drop shipped to prod costs more than a week of prompt tuning in staging.
"""

STRUCTURED_MD = """\
## Why structured outputs

Free-form JSON from models breaks parsers. Structured outputs constrain generation to a schema so downstream code stays simple.

## JSON Schema example

```json
{
  "type": "object",
  "properties": {
    "summary": { "type": "string" },
    "severity": { "enum": ["low", "medium", "high"] },
    "follow_up": { "type": "boolean" }
  },
  "required": ["summary", "severity"]
}
```

## Validation loop

Generate → validate with Pydantic → on failure, retry once with the validation error in context. Cap retries to avoid runaway cost.

## Versioning

Treat schemas like API contracts. Bump a `schema_version` field when fields change.
"""

CHUNKING_MD = """\
## The chunking problem

Chunking is the highest-leverage RAG knob and the least discussed. Bad chunks cap quality no matter which model you use.

## Strategies we tested

### Fixed windows

Fast to implement. Breaks code blocks and tables unless you pre-process markdown.

### Structure-aware splits

Split on headings first, then paragraphs. Preserves sections for citation.

## Measuring success

Track **answerable rate** on a fixed question set — not embedding cosine similarity alone.
"""

TOOL_CALLING_MD = """\
## Patterns that survived production

### Read-only default

Agents start without write tools. Escalation paths unlock mutations after human approval.

### Argument validation

Validate tool args with the same schemas you use in HTTP APIs. The model will invent plausible-looking garbage.

## Failure handling

Return structured errors to the model (`code`, `message`, `retryable`). Unstructured stack traces encourage retry loops.
"""

ARTICLES = [
    {
        "slug": "production-rag-pipeline",
        "title": "Building a Production RAG Pipeline",
        "excerpt": "Indexing, retrieval thresholds, and the failure modes nobody mentions in tutorials — from a system we actually run.",
        "content_markdown": RAG_PIPELINE_MD,
        "reading_time": 12,
        "category_slug": "rag",
        "seo_keywords": "RAG, embeddings, retrieval, pgvector",
        "featured": True,
        "project_slug": "orbitx-voice-pipeline",
    },
    {
        "slug": "chunking-strategies-rag",
        "title": "Chunking Strategies That Actually Work",
        "excerpt": "Fixed windows vs. structure-aware splits — and how we measure whether chunks are good enough.",
        "content_markdown": CHUNKING_MD,
        "reading_time": 7,
        "category_slug": "rag",
        "seo_keywords": "chunking, indexing, markdown",
    },
    {
        "slug": "multi-agent-orchestration",
        "title": "Designing Multi-Agent Orchestration",
        "excerpt": "A practical agent loop: planning, tools, observability, and when simpler code wins.",
        "content_markdown": AGENTS_MD,
        "reading_time": 9,
        "category_slug": "agents",
        "seo_keywords": "agents, tools, orchestration",
        "featured": True,
    },
    {
        "slug": "tool-calling-production",
        "title": "Tool-Calling Patterns in Production",
        "excerpt": "Read-only defaults, schema validation, and structured errors that stop retry storms.",
        "content_markdown": TOOL_CALLING_MD,
        "reading_time": 6,
        "category_slug": "agents",
        "seo_keywords": "tool calling, validation, agents",
    },
    {
        "slug": "langgraph-state-machines",
        "title": "State Machines with LangGraph",
        "excerpt": "Explicit state, conditional edges, and checkpointing for workflows that survive deploys.",
        "content_markdown": LANGGRAPH_MD,
        "reading_time": 8,
        "category_slug": "langgraph",
        "seo_keywords": "LangGraph, state, workflows",
    },
    {
        "slug": "choosing-a-vector-database",
        "title": "Choosing a Vector Database",
        "excerpt": "Recall, metadata filters, hybrid search, and migration traps — without vendor hype.",
        "content_markdown": VECTOR_MD,
        "reading_time": 7,
        "category_slug": "vector-dbs",
        "seo_keywords": "vector, hybrid search, embeddings",
    },
    {
        "slug": "mcp-servers-zero-to-ship",
        "title": "MCP Servers from Zero to Ship",
        "excerpt": "A minimal MCP server, security defaults, and a checklist before you share it with the team.",
        "content_markdown": MCP_MD,
        "reading_time": 6,
        "category_slug": "mcp",
        "seo_keywords": "MCP, tools, IDE",
    },
    {
        "slug": "prompt-engineering-reliability",
        "title": "Prompt Engineering for Reliability",
        "excerpt": "Templates, golden evals, and why boring prompts outperform clever ones in production.",
        "content_markdown": PROMPT_MD,
        "reading_time": 5,
        "category_slug": "prompt-engineering",
        "seo_keywords": "prompts, evals, templates",
    },
    {
        "slug": "structured-outputs-json-schema",
        "title": "Structured Outputs with JSON Schema",
        "excerpt": "Schema-first generation, Pydantic validation, and versioning contracts with downstream services.",
        "content_markdown": STRUCTURED_MD,
        "reading_time": 6,
        "category_slug": "structured-outputs",
        "seo_keywords": "JSON schema, structured output, validation",
    },
]


def ensure_categories(db) -> dict[str, int]:
    learn_theme = db.scalar(select(Theme).where(Theme.slug == "learn"))
    theme_id = learn_theme.id if learn_theme else None
    out: dict[str, int] = {}
    for data in CATEGORIES:
        cat = db.scalar(select(Category).where(Category.slug == data["slug"]))
        if cat is None:
            cat = Category(name=data["name"], slug=data["slug"], theme_id=theme_id)
            db.add(cat)
            db.flush()
        out[data["slug"]] = cat.id
    return out


def resolve_author_id(db) -> int | None:
    user = db.scalar(select(User).order_by(User.id).limit(1))
    return user.id if user else None


def resolve_project_id(db, slug: str | None) -> int | None:
    if not slug:
        return None
    project = db.scalar(select(Project).where(Project.slug == slug))
    return project.id if project else None


def seed_article(db, data: dict, category_ids: dict[str, int], author_id: int | None) -> str:
    slug = data["slug"]
    existing = db.scalar(select(Article).where(Article.slug == slug))
    category_id = category_ids.get(data["category_slug"])
    project_id = resolve_project_id(db, data.get("project_slug"))

    fields = {
        "title": data["title"],
        "excerpt": data["excerpt"],
        "content_markdown": data["content_markdown"],
        "reading_time": data["reading_time"],
        "category_id": category_id,
        "author_id": author_id,
        "project_id": project_id,
        "seo_keywords": data.get("seo_keywords"),
        "featured": data.get("featured", False),
        "published": True,
        "visibility": ContentVisibility.PUBLIC,
    }

    if existing:
        for key, value in fields.items():
            setattr(existing, key, value)
        return "updated"

    db.add(Article(slug=slug, **fields))
    return "created"


def main() -> None:
    db = SessionLocal()
    try:
        category_ids = ensure_categories(db)
        author_id = resolve_author_id(db)
        created = updated = 0

        for item in ARTICLES:
            status = seed_article(db, item, category_ids, author_id)
            if status == "created":
                created += 1
            else:
                updated += 1

        db.commit()
        print(f"Academy seed complete: {created} created, {updated} updated.")
        print(f"Categories: {len(category_ids)}")
        print("Open http://localhost:3000/learn")
        print("Featured article: http://localhost:3000/learn/production-rag-pipeline")
    finally:
        db.close()


if __name__ == "__main__":
    main()
