# Seattle Policy Agent

A policy chat agent built incrementally, starting with direct LLM interaction and evolving into a full RAG system.

## Phase 1: Direct LLM Chat

The current phase focuses on establishing a direct connection to OpenAI models to test prompting strategies and parameters.

### Setup

1.  **Prerequisites**: Python 3.9+
2.  **Installation**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt  # (Create this if needed, currently manual install)
    # Or: pip install openai python-dotenv
    ```
3.  **Configuration**:
    - Create a `.env` file in the root.
    - Add your API key: `OPENAI_API_KEY=sk-...`

### Usage

Run the chat experiment script:

```bash
python src/chat_experiment.py
```

- Type your message to chat.
- Type `quit`, `exit`, or `bye` to end the session.
- Logs are saved to `experiment_logs.jsonl`.

## RAG Agent Reference

This project references code from the `RAG Agent` folder but maintains its own independent codebase in `src/`.
