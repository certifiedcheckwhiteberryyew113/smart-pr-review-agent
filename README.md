# Smart PR Review Agent
## Architecture
```mermaid
flowchart TD
    UI["Frontend — React + Vite\nPR URL · Mode selector · Live feed · Diff viewer"]
    API["FastAPI Backend — Render\n/review · /stream · /approve · /health"]
    LG["LangGraph Workflow\nreview_only · human_in_loop · auto_pilot"]
    IDX["Indexer\ntree-sitter + ChromaDB"]
    REV["Reviewer\ninline PR comments"]
    BUG["Bug Hunter\ndeep RAG search"]
    ISS["Issue Raiser\nGitHub issues"]
    FIX["Fix Drafter\npatch + run tests"]
    MCP["GitHub MCP\nremote server"]
    CHROMA["ChromaDB\nvector store"]
    GROQ["Groq LLM\nllama-3.3-70b"]
    SMITH["LangSmith\nfull traces"]
    PG["Supabase\nPostgres checkpoints"]
    GH["GitHub App\nsmart-pr-review-bot"]

    UI -->|SSE / HTTP| API
    API --> LG
    LG --> IDX
    LG --> REV
    LG --> BUG
    LG --> ISS
    LG --> FIX
    IDX --> CHROMA
    REV --> GROQ
    BUG --> CHROMA
    BUG --> GROQ
    FIX --> GROQ
    API --> MCP
    MCP --> GH
    LG --> PG
    REV --> SMITH
    BUG --> SMITH
    FIX --> SMITH

    style UI fill:#185FA5,color:#fff
    style API fill:#0F6E56,color:#fff
    style LG fill:#534AB7,color:#fff
    style IDX fill:#854F0B,color:#fff
    style REV fill:#854F0B,color:#fff
    style BUG fill:#854F0B,color:#fff
    style ISS fill:#854F0B,color:#fff
    style FIX fill:#854F0B,color:#fff
    style MCP fill:#3B6D11,color:#fff
    style CHROMA fill:#3B6D11,color:#fff
    style GROQ fill:#3B6D11,color:#fff
    style SMITH fill:#3B6D11,color:#fff
    style PG fill:#5F5E5A,color:#fff
    style GH fill:#5F5E5A,color:#fff
```

FastAPI backend with LangGraph workflow, GitHub integration, and a Vite + React UI.

## Setup

1. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`, `GITHUB_TOKEN`, and GitHub app fields.
2. Backend: install `requirements.txt`, set `PYTHONPATH` to the repo root, run `uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000`.
3. Frontend: `cd frontend`, `npm install`, `npm run dev` (proxies API to port 8000).

## API

- `GET /health`
- `POST /review`
- `GET /stream/{thread_id}` (SSE)
- `POST /approve`
