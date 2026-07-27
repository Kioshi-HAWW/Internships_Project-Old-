# PRD — Personal Library RAG Assistant

## 1. What We're Building
A Retrieval-Augmented Generation (RAG) system that lets a user ask questions
in natural language and get answers grounded in their **own document
library** (books, notes, PDFs, docs stored in Google Drive). The system
retrieves relevant chunks from a vector store and uses an AI agent (Gemini)
to synthesize a grounded, cited answer — not a hallucinated one.

Hosted on **Render** as a web service (API + optional simple chat UI).

## 2. Problem Statement
The user has a large personal library scattered across Google Drive. Finding
answers currently means manually searching/skimming files. We want a system
that:
- Ingests documents from Drive automatically
- Chunks + embeds them into a searchable vector index
- Lets an AI agent search that index as a **tool** and answer questions
  using only (or primarily) retrieved content

## 3. Target Users
- Primary: the project owner (personal knowledge base assistant)
- Secondary (future): small team/friends who want to query a shared library

## 4. Core Features (MVP)
1. **Google Drive connector** — authenticate, list files in a target
   folder, download supported files (pdf, docx, gdoc, txt, md).
2. **Ingestion pipeline** — extract text → chunk → embed → upsert into
   vector store, with metadata (source file, page, drive link).
3. **Vector store** — persistent, queryable by similarity + metadata filter.
4. **RAG Agent** — Gemini-based agent with a `search_library` tool that:
   - Takes a query
   - Retrieves top-k chunks from the vector store
   - Returns them to Gemini to compose a cited answer
5. **Chat API endpoint** — `POST /chat` takes a user question, runs the
   agent loop, returns answer + sources.
6. **Re-ingestion** — ability to re-sync when files are added/changed in
   Drive (manual trigger for MVP; scheduled later).
7. **Deployment** — deployed and reachable on Render.

## 5. Out of Scope (MVP)
- Multi-user auth / accounts
- Real-time Drive webhook sync (poll/manual trigger is fine for v1)
- Editing documents from the app
- Fine-tuning any model
- Support for images/audio/video content

## 6. Success Criteria
- User can ask a question and get an answer that correctly cites the
  source document(s) it came from.
- Ingesting a new file into the Drive folder and re-running ingestion makes
  it queryable within one pipeline run.
- API is live and stable on Render (no cold-start crashes, no timeout on
  normal queries).

## 7. Key Risks / Open Questions
- Render free/starter tier has **ephemeral disk** — vector DB must be an
  external hosted service (not local Chroma on disk), or persisted via a
  Render Disk (paid) — see arch.md.
- Google Drive API auth (OAuth vs. Service Account) needs to be decided
  early — see rules.md.
- Cost control on embeddings + LLM calls as the library grows.
