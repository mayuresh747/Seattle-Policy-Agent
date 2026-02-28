# Changelog — Seattle Policy Agent

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Planned
- Phase 2: RAG integration with vector store
- `requirements.txt` for reproducible installs
- Git repository initialization
- Parameter experimentation (temperature, model variants)

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
