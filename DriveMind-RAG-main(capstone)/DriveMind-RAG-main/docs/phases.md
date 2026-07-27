# PHASES — Build Plan

Each phase should end with something runnable/testable before moving on.
Update `memory.md` after every phase (or sub-step) is completed.

## Phase 0 — Setup (all free, no card required)
- [x] Create repo + folder structure (per arch.md)
- [x] Set up virtualenv, `requirements.txt`
- [x] Create `.env.example`, `config.py`
- [x] Create a **Qdrant Cloud** free-forever cluster + collection (empty)
- [x] Create Google Cloud project, enable Drive API, create Service
      Account, share target Drive folder with it
- [x] Get a **Gemini API key** from Google AI Studio (free tier)
- [x] Confirm `sentence-transformers` installs and loads
      `all-MiniLM-L6-v2` locally (no key needed)

## Phase 1 — Drive Ingestion
- [x] `drive_service.py`: authenticate, list files in target folder
- [x] Download/export supported file types (pdf, docx, gdoc→text, txt, md)
- [x] Basic CLI script (`scripts/ingest_drive.py`) that prints file list
- [x] Test: confirm it correctly lists & downloads a few real files

## Phase 2 — Chunk + Embed + Store
- [x] `chunking_service.py`: split extracted text into chunks w/ overlap
- [x] `embedding_service.py`: call local sentence-transformers embeddings (`all-MiniLM-L6-v2`) for each chunk
- [x] `vectorstore_service.py`: upsert chunks + metadata into Qdrant
- [x] Wire into `scripts/ingest_drive.py` end-to-end
- [x] Test: run full ingestion on a small folder, confirm vectors land in
      Qdrant with correct metadata

## Phase 3 — Retrieval
- [x] `vectorstore_service.py`: add `search(query, top_k)` function
- [x] Test: manually query and confirm relevant chunks come back for a
      known question

## Phase 4 — Agent + Tool
- [x] Define `search_library` tool/function schema (Gemini function
      calling format)
- [x] `agent_service.py`: Gemini tool-use loop (send question → function
      call → function result → final answer)
- [x] Test: ask a question in a script, confirm agent calls the tool and
      returns a cited answer

## Phase 5 — API Layer
- [x] `POST /chat` route wired to `agent_service`
- [x] `POST /ingest` route wired to ingestion pipeline
- [x] `GET /health`
- [x] Test via FastAPI TestClient (12/12 tests passing)

## Phase 6 — Deploy to Render ✅
- [x] `render.yaml` + Dockerfile with Docker runtime (created)
- [x] Set all env vars in Render dashboard (GEMINI_API_KEY, QDRANT_API_KEY, QDRANT_URL, GOOGLE_SERVICE_ACCOUNT_B64, GOOGLE_DRIVE_FOLDER_ID)
- [x] Deploy succeeded — service live at https://drivemind-rag-1.onrender.com
- [x] `/health` returns `{"status":"ok"}` ✅
- [x] Run `/ingest` in production, then test `/chat` (Validated asynchronous execution, batched embeddings, and zero OOM issues)

## Phase 7 — Polish (post-MVP)
- [ ] Simple chat UI (optional) or Postman collection for now
- [ ] Scheduled re-ingestion (cron on Render or manual trigger button)
- [ ] Better error surfaces, rate limiting
- [ ] Basic auth on the API if it'll be shared

---
**Rule for every AI session working on this project:** before doing
anything, read the 6 `.md` files in `docs/` (`prd.md`, `arch.md`, `rules.md`, `phases.md`, `design.md`, `memory.md`) to see current phase/status and pick up
exactly where the last session left off. After finishing a step, update all 6 `docs/*.md` files.
