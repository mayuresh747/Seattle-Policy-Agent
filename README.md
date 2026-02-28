# Seattle Policy Agent

A policy chat agent built incrementally, starting with direct LLM interaction and evolving into a full RAG system.

## Current Phase: Chat Agent UI & Backend

The current phase features a standalone web interface connected to a FastAPI backend. It interacts directly with OpenAI (no RAG retrieval yet), strictly following instructions configured via YAML.

### Setup

1.  **Prerequisites**: Python 3.9+
2.  **Installation**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Configuration**:
    - Create a `.env` file in the root.
    - Add your API key: `OPENAI_API_KEY=sk-...`
    - Modify `src/chat_agent/agent_config.yaml` to adjust the LLM model, temperature, system prompts, or UI text. Note: `gpt-5.1` configuration will reflect whatever model you've chosen in your YAML.

### Usage

Run the local development server:

```bash
python scripts/run_chat_agent.py
```

Then, open your browser and navigate to:
**[http://localhost:8000](http://localhost:8000)**

- Type your message to chat, or use one of the example queries.
- Click the gear icon in the top-right to edit System Instructions or Temperature on the fly.
- Logs are saved to `chat_agent_logs.jsonl` (if enabled in config).

## RAG Agent Reference
This project references code from the `RAG Agent` folder but maintains its own independent codebase in `src/`. No files inside `RAG Agent/` may be edited or imported directly.
