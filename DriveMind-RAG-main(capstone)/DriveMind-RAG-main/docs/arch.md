# ARCH — Architecture & Tech Stack

> **Cost constraint: $0.** Every piece of this stack must run on a
> genuinely free tier. No paid API keys, no paid Render plan, no paid
> vector DB plan. Note: a "ChatGPT Go" subscription does **not** include
> OpenAI API access — API billing is always separate from any ChatGPT
> consumer plan — so it can't be used here. Google's Gemini API has an
> actual free tier for developers, which is what we use instead.

## 1. Tech Stack

| Layer            | Choice                                   | Why |
|-------------------|-------------------------------------------|-----|
| Backend framework | **FastAPI** (Python)                      | Async, free to self-host, huge RAG ecosystem |
| Source docs       | **Google Drive API**                      | User's library lives there; free |
| Parsing           | `pypdf`, `python-docx`, Drive export for Gdocs | Cover pdf/docx/gdoc/txt |
| Chunking          | LangChain `RecursiveCharacterTextSplitter`| Battle-tested, simple, free (local lib) |
| Embeddings        | **Gemini API — free tier** (`models/gemini-embedding-001`) | Replaced local models to avoid 512MB RAM OOM limits on Render free tier. Free daily quota. |
| Vector store      | **Qdrant Cloud — Free Forever tier** (1GB) | Persistent, hosted, no credit card required — avoids Render's ephemeral disk problem |
| Agent / chat model| **Google Gemini API — free tier** (e.g. `gemini-3.5-flash` or current free-tier model) | Genuinely free daily quota, supports function/tool calling needed for the agent |
| Agent framework   | Hand-rolled tool-use loop via `google-generativeai` SDK | Keep it simple, no heavy framework |
| Hosting           | **Render Free Web Service**               | $0, per requirement — see limitations below |
| Secrets           | Render Environment Variables              | API keys never in repo |

## 2. Free-Tier Limitations to Design Around
- **Render free web services sleep after ~15 min of inactivity** and take
  ~30-60s to "wake up" on the next request (cold start). Fine for a
  personal tool, just expect the first message after idle time to be
  slow.
- **No free cron jobs on Render.** Scheduled auto re-ingestion isn't
  free, so re-ingestion stays a manually-triggered `POST /ingest` call
  (you hit it yourself, or trigger it from your machine/phone when you
  add new files to Drive).
- **Gemini free tier has request-per-minute / per-day limits.** Fine for
  single-user personal use, but we batch our chunk embedding requests
  to stay within the 15 RPM limit.
- **Qdrant free tier caps at 1GB** — more than enough for a personal text
  library (a 1GB collection is roughly hundreds of thousands of chunks).

> If any of these limits become a real problem later, the fix is a $7/mo
> Render plan (no sleep, real cron) — but the whole system is designed to
> run at $0 first.

## 2. High-Level Flow

```
[Google Drive Folder]
        │  (list + download files)
        ▼
[Ingestion Pipeline]  ── extract text ── chunk ── embed (Gemini API) ──► [Qdrant Vector Store]
                                                                                 ▲
                                                                                 │ search_library tool
[User] ──question──► [/chat API] ──► [Gemini Agent Loop] ─────────────────────┘
                                          │
                                          ▼
                                 [Answer + Sources] ──► [User]
```

## 3. Agent Loop (per request)
1. User sends question → `/chat`.
2. Gemini receives the question + `search_library` function/tool definition.
3. Gemini decides to call `search_library(query, top_k)`.
4. Backend embeds the query using Gemini Embedding API (`gemini-embedding-001`),
   searches Qdrant, returns chunks + metadata (source file name, drive
   link, chunk text) as the function result.
5. Gemini reads the result, composes final answer citing sources.
6. Backend returns `{ answer, sources[] }` to the user.

## 4. Folder / File Structure

```
project-root/
├── app/
│   ├── main.py                    # FastAPI app entrypoint
│   ├── core/
│   │   ├── config.py              # env vars, settings
│   │   └── logging.py
│   ├── api/
│   │   └── routes/
│   │       ├── chat.py            # POST /chat
│   │       ├── ingest.py          # POST /ingest (trigger sync)
│   │       └── health.py          # GET /health
│   ├── services/
│   │   ├── drive_service.py       # list/download from Google Drive
│   │   ├── chunking_service.py    # text splitting
│   │   ├── embedding_service.py   # Gemini Embeddings API
│   │   ├── vectorstore_service.py # Qdrant client wrapper
│   │   └── agent_service.py       # Claude agent loop + tool defs
│   ├── tools/
│   │   └── search_library_tool.py # tool schema + handler
│   └── models/
│       └── schemas.py             # Pydantic request/response models
├── scripts/
│   └── ingest_drive.py            # standalone CLI ingestion runner
├── tests/
│   ├── test_chunking.py
│   ├── test_vectorstore.py
│   └── test_agent.py
├── docs/
│   ├── prd.md
│   ├── arch.md
│   ├── rules.md
│   ├── phases.md
│   ├── design.md
│   └── memory.md
├── requirements.txt
├── render.yaml                    # Render deployment config
├── .env.example
├── .gitignore
└── README.md
```

## 5. Data Model (vector store payload per chunk)
```json
{
  "id": "uuid",
  "vector": [ ...float embeddings... ],
  "payload": {
    "text": "chunk text",
    "source_file": "filename.pdf",
    "drive_file_id": "abc123",
    "drive_link": "https://drive.google.com/...",
    "chunk_index": 4,
    "page": 12
  }
}
```

## 6. API Endpoints (MVP)
- `POST /ingest` — trigger a Drive sync + embedding run
- `POST /chat` — `{ "message": "..." }` → `{ "answer": "...", "sources": [...] }`
- `GET /health` — uptime check for Render

## 7. Deployment on Render
- **Free Web Service**, build command `pip install -r requirements.txt`
- Start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Env vars set in Render dashboard (all free-tier keys, no billing
  required): `GEMINI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`,
  `GOOGLE_SERVICE_ACCOUNT_JSON`
- No credit card needed anywhere in this stack: Render free plan, Google
  AI Studio (Gemini) free API key, Qdrant Cloud free cluster, Google
  Cloud service account (free) all sign up without billing info.
