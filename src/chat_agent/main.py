"""
FastAPI Chat Server — SSE streaming chat with settings management.
Adapted from RAG Agent pattern, without RAG retrieval or auth.
"""

import json
import time
import datetime
from pathlib import Path
from typing import Optional, Dict, List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.chat_agent.config import get_config
from src.chat_agent.chat_engine import chat_stream


# ── Load config ──────────────────────────────────────────────────────────
cfg = get_config()


# ── App setup ────────────────────────────────────────────────────────────
app = FastAPI(title=cfg.app_title, version="1.0.0")

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── In-memory session state ──────────────────────────────────────────────
sessions: Dict[str, Dict] = {}


def get_session_state(session_id: str) -> Dict:
    """Get or create session state."""
    if session_id not in sessions:
        sessions[session_id] = {
            "system_prompt": cfg.system_prompt,
            "conversation_history": [],
            "temperature": cfg.llm_temperature,
        }
    return sessions[session_id]


# ── Request / Response models ────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: str


class SettingsRequest(BaseModel):
    session_id: str
    system_prompt: str
    temperature: Optional[float] = None


# ── Logging ──────────────────────────────────────────────────────────────

def log_interaction(session_id: str, question: str, answer: str,
                    input_tokens: int, output_tokens: int,
                    temperature: float, duration_ms: int):
    """Append interaction to JSONL log file (if enabled)."""
    if not cfg.logging_enabled:
        return
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "session_id": session_id,
        "question": question,
        "answer": answer,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "temperature": temperature,
        "duration_ms": duration_ms,
    }
    try:
        with open(cfg.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass  # Don't crash on logging failures


# ── Routes ───────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serve the chat UI."""
    index_path = STATIC_DIR / "index.html"
    return HTMLResponse(content=index_path.read_text(), status_code=200)


@app.get("/api/config")
async def get_ui_config():
    """Return UI-facing config values (title, subtitle, examples, etc.)."""
    return {
        "title": cfg.app_title,
        "subtitle": cfg.app_subtitle,
        "welcome_message": cfg.welcome_message,
        "example_queries": cfg.example_queries,
    }


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Stream a chat response via SSE."""
    state = get_session_state(request.session_id)

    full_tokens: List[str] = []
    usage_info = {"input_tokens": 0, "output_tokens": 0}
    start_time = time.time()

    def event_generator():
        for event in chat_stream(
            user_message=request.message,
            conversation_history=state["conversation_history"],
            system_prompt=state["system_prompt"],
            temperature=state["temperature"],
        ):
            if event["type"] == "token":
                full_tokens.append(event["data"])
            elif event["type"] == "usage":
                usage_info.update(event.get("data", {}))
            elif event["type"] == "done":
                # Save to conversation history
                answer_text = "".join(full_tokens)
                state["conversation_history"].append(
                    {"role": "user", "content": request.message}
                )
                state["conversation_history"].append(
                    {"role": "assistant", "content": answer_text}
                )
                # Log interaction
                duration_ms = int((time.time() - start_time) * 1000)
                log_interaction(
                    session_id=request.session_id,
                    question=request.message,
                    answer=answer_text,
                    input_tokens=usage_info["input_tokens"],
                    output_tokens=usage_info["output_tokens"],
                    temperature=state["temperature"],
                    duration_ms=duration_ms,
                )
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/settings")
async def get_settings(session_id: str):
    """Get current system prompt and temperature."""
    state = get_session_state(session_id)
    return {
        "system_prompt": state["system_prompt"],
        "temperature": state["temperature"],
    }


@app.put("/api/settings")
async def update_settings(request: SettingsRequest):
    """Update the system prompt and/or temperature."""
    state = get_session_state(request.session_id)
    state["system_prompt"] = request.system_prompt
    if request.temperature is not None:
        state["temperature"] = max(0.0, min(2.0, request.temperature))
    return {
        "status": "ok",
        "system_prompt": state["system_prompt"],
        "temperature": state["temperature"],
    }


@app.delete("/api/chat/history")
async def clear_history(session_id: str):
    """Clear conversation history for a session."""
    if session_id in sessions:
        sessions[session_id]["conversation_history"] = []
    return {"status": "ok", "message": "Conversation cleared", "session_id": session_id}
