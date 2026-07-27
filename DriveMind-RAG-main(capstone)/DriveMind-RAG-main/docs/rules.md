# RULES — Conventions, Libraries, Boundaries

## 1. Libraries — Use
- **FastAPI** for the API layer
- **pydantic** for all request/response schemas and config validation
- **httpx** for outbound HTTP calls (not `requests`, for async support)
- **google-generativeai** official SDK for the Gemini agent/chat model
  (free tier)
- **Gemini Embeddings API** (`models/gemini-embedding-001`) for **free**
  embeddings (batched to respect 15 RPM limits) — replaced local models to prevent 512MB RAM OOMs on Render.
- **qdrant-client** for vector store (free cloud cluster)
- **google-api-python-client** + `google-auth` for Drive access
- **langchain-text-splitters** (lightweight, just for chunking — do NOT
  pull in full LangChain agent/orchestration layers unless a real need
  appears)
- **python-dotenv** for local env loading
- **pytest** for tests

## 2. Libraries / Services — Avoid
- **No paid API keys anywhere** — this project has a hard $0 budget.
  Before adding any new dependency, check it has a genuinely free tier
  with no credit card requirement.
- Avoid OpenAI or Anthropic APIs unless the user explicitly decides to
  start paying — a "ChatGPT Go" or similar consumer chat subscription
  does **not** grant API credits, so don't assume it covers API calls.
- Avoid full **LangChain agents / LangGraph** for the MVP — the tool-use
  loop is simple enough to hand-roll with the Gemini SDK; adding a heavy
  orchestration framework early adds complexity and hides bugs.
- Avoid **Chroma running locally on Render's disk** — ephemeral storage
  will lose the index on redeploy/restart. Use Qdrant Cloud's free
  cluster instead.
- Avoid mixing sync and async DB/HTTP clients in the same request path.
- Avoid hardcoding API keys, folder IDs, or file paths — everything
  configurable goes through `app/core/config.py` + env vars.
- Avoid global mutable state for the vector store client — instantiate
  once and inject/reuse it (FastAPI dependency).
- Avoid relying on Render cron for scheduling (not free) — keep
  re-ingestion as a manually-triggered endpoint for now.

## 3. Google Drive Auth
- Use a **Service Account** with a shared target folder (simplest for a
  personal/single-user project — no OAuth consent flow needed).
- Store the service account JSON as a Render env var (base64-encoded),
  never commit it to the repo.

## 4. Chunking Rules
- Default chunk size: ~800–1000 tokens, ~150 token overlap. Tune per
  document type (dense PDFs vs. plain notes) later, not in MVP.
- Always store metadata (source file, drive link, chunk index) with every
  chunk — answers must be traceable back to source.

## 5. Error Handling
- Every service function that calls an external API (Drive, OpenAI,
  Anthropic, Qdrant) must:
  - Catch and log the specific exception
  - Return a clear error to the caller (no silent failures)
  - Never crash the whole ingestion run over a single bad file — skip and
    log, continue with the rest
- API layer (`routes/`) converts service exceptions into proper HTTP
  status codes (400 for bad input, 502 for upstream failures, 500 for
  unexpected).
- Never leak stack traces or raw API keys/secrets in HTTP responses.

## 6. AI Agent Boundaries
- The agent **must only answer from retrieved context** for
  library-specific questions. If retrieval returns nothing relevant, the
  agent should say so rather than guessing.
- The agent should always cite which source file(s) an answer came from.
- Keep `top_k` retrieval bounded (e.g. 5–8 chunks) to control token cost
  and avoid context dilution.
- The `search_library` tool is read-only. Do not give the agent any tool
  that can write/delete Drive files or vector store data in the MVP.
- Log every tool call (query + result count) for debugging.

## 7. Secrets & Config
- All secrets via environment variables, documented in `.env.example`
  (with placeholder values only).
- `config.py` is the single source of truth for reading env vars — no
  `os.environ` calls scattered through the codebase.

## 8. Git / Repo Hygiene
- `.gitignore` must exclude `.env`, `__pycache__/`, any downloaded Drive
  files cache, and service account JSON.
- Commit messages reference which phase (from phases.md) the work belongs
  to.

## 9. Documentation Sync
- Read all 6 markdown files in `docs/` (`prd.md`, `arch.md`, `rules.md`, `phases.md`, `design.md`, `memory.md`) before starting any phase.
- Always update the 6 markdown files in `docs/` after completing each phase so that future sessions resume directly from the updated documentation.

