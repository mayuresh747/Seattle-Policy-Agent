# Changelog — Seattle Policy Agent

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Planned
- Phase 3: RAG integration with vector store
- PDF ingestion pipeline for WA and Seattle codes

---

## [0.3.0] — 2026-02-27

### Added
- **Chat Agent UI and Backend**: Built a fully functional Web UI serving OpenAI SSE streams, mirroring the premium RAG Agent UI.
- All configurations (model parameters, system instructions, UI texts, example queries) externalized to `src/chat_agent/agent_config.yaml`.
- Launch script `scripts/run_chat_agent.py` for starting the FastAPI application.
- `.gitignore` robustly configured to ignore `.agent/`, `RAG Agent/`, `.venv/`, and sensitive `.env` files.

### Removed
- Legacy testing file `src/chat_experiment.py` and empty folders `docs/` and `tests/`.

---

## [0.2.0] — 2026-02-18

### Added
- `.agent/` system with **12 agents** and **6 workflows** for structured AI-assisted development
- `tests/reproduce_memory.py` — regression test for chat context retention
- Workflow: `workflow_memory_sync` for state/documentation synchronization
- `CHANGELOG.md` (this file)

### Fixed
- **Chat memory bug**: Model incorrectly claimed amnesia about prior conversation turns
  - Root cause: system prompt did not instruct model to use conversation history
  - Fix: updated system prompt in `src/chat_experiment.py` to explicitly enable recall

---

## [0.1.0] — 2026-02-17

### Added
- `src/chat_experiment.py` — multi-turn OpenAI GPT-4o chat with:
  - Session ID generation (UUID)
  - Full conversation history passed on every turn
  - JSONL interaction logging to `experiment_logs.jsonl`
  - Lazy OpenAI client initialization
- `src/config.py` — loads `OPENAI_API_KEY` from `.env` via `python-dotenv`
- `README.md` — project overview and Phase 1 setup instructions
- `.agent/rules/ignorefolder.md` — protection rule for `RAG Agent` reference folder
