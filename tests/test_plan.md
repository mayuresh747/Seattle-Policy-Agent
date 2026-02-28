# Chat Agent Test Plan

## Overview
This test plan defines the automated testing strategy for the Seattle Policy Agent's FastAPI backend and configuration management. The goal is to ensure the UI backend is stable, configuration loads correctly, and API endpoints behave as expected.

## Scope
1. **Configuration (`src.chat_agent.config`)**
   - Verify `agent_config.yaml` is parsed correctly.
   - Verify environment variables (e.g., `OPENAI_API_KEY`) are loaded.
2. **API Endpoints (`src.chat_agent.main`)**
   - `GET /` — serves index.html.
   - `GET /api/config` — returns sanitized config settings.
   - `GET /api/settings` — returns current UI settings.
   - `DELETE /api/chat/history` — clears session history.
3. **Chat Engine (`src.chat_agent.chat_engine`)**
   - (Mocked) Verify SSE stream formatting.

## Test Scripts
- `tests/test_config.py`
- `tests/test_api.py`

## Execution Strategy
- Framework: `pytest`
- API Testing: `httpx.AsyncClient` or `fastapi.testclient.TestClient`
- We will execute the tests. If failures occur, we will enter the autonomous repair loop.
