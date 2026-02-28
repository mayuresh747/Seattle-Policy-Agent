"""
Chat Engine — OpenAI streaming chat without RAG.
Adapted from the RAG Agent's rag_chain.py pattern.
"""

from typing import Optional, Generator
from openai import OpenAI

from src.chat_agent.config import OPENAI_API_KEY, get_config

# ── Lazy client ──────────────────────────────────────────────────────────
_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


# ── Streaming chat ───────────────────────────────────────────────────────

def chat_stream(
    user_message: str,
    conversation_history: list,
    system_prompt: Optional[str] = None,
    temperature: Optional[float] = None,
) -> Generator[dict, None, None]:
    """
    Stream a chat response from OpenAI.

    Yields dicts with keys:
        - {"type": "token", "data": "..."}   — streamed token
        - {"type": "usage", "data": {...}}   — token usage stats
        - {"type": "done"}                   — stream finished
        - {"type": "error", "data": "..."}   — error message
    """
    cfg = get_config()
    system = system_prompt or cfg.system_prompt
    temp = temperature if temperature is not None else cfg.llm_temperature

    # Build messages with conversation memory
    messages = [{"role": "system", "content": system}]

    # Trim conversation history to memory size
    max_messages = cfg.conversation_memory_size * 2  # pairs of user+assistant
    recent_history = conversation_history[-max_messages:]
    messages.extend(recent_history)

    messages.append({"role": "user", "content": user_message})

    # Stream from OpenAI
    try:
        client = _get_client()
        stream = client.chat.completions.create(
            model=cfg.llm_model,
            messages=messages,
            temperature=temp,
            max_completion_tokens=cfg.llm_max_tokens,
            stream=True,
            stream_options={"include_usage": True},
        )

        usage_data = None
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield {"type": "token", "data": chunk.choices[0].delta.content}

            # Capture usage from the final chunk
            if hasattr(chunk, "usage") and chunk.usage is not None:
                usage_data = {
                    "input_tokens": chunk.usage.prompt_tokens or 0,
                    "output_tokens": chunk.usage.completion_tokens or 0,
                }

        if usage_data:
            yield {"type": "usage", "data": usage_data}
        yield {"type": "done"}

    except Exception as e:
        yield {"type": "error", "data": f"LLM error: {e}"}
