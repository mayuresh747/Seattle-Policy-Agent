"""
Config loader — reads agent_config.yaml and .env, exposes typed values.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import yaml

# ── Paths ────────────────────────────────────────────────────────────────
AGENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = AGENT_DIR.parent.parent
CONFIG_PATH = AGENT_DIR / "agent_config.yaml"

# ── Load .env ────────────────────────────────────────────────────────────
load_dotenv(PROJECT_ROOT / ".env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def load_config() -> dict:
    """Load the YAML configuration file."""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def get_config():
    """Return a convenience object with all config values."""
    raw = load_config()
    return _Config(raw)


class _Config:
    """Typed access to agent_config.yaml values."""

    def __init__(self, raw: dict):
        self._raw = raw

        # App
        app = raw.get("app", {})
        self.app_title: str = app.get("title", "Chat Agent")
        self.app_subtitle: str = app.get("subtitle", "Your intelligent AI assistant")
        self.app_port: int = int(app.get("port", 8000))
        self.welcome_message: str = app.get("welcome_message", "Ask me anything.")

        # LLM
        llm = raw.get("llm", {})
        self.llm_model: str = llm.get("model", "gpt-4o")
        self.llm_temperature: float = float(llm.get("temperature", 0.7))
        self.llm_max_tokens: int = int(llm.get("max_tokens", 2048))
        self.conversation_memory_size: int = int(llm.get("conversation_memory_size", 20))

        # System prompt
        self.system_prompt: str = raw.get("system_prompt", "You are a helpful assistant.")

        # Example queries
        self.example_queries: list = raw.get("example_queries", [])

        # Logging
        log = raw.get("logging", {})
        self.logging_enabled: bool = log.get("enabled", True)
        self.log_file: str = log.get("file", "chat_agent_logs.jsonl")

    def __repr__(self):
        return (
            f"Config(model={self.llm_model}, temp={self.llm_temperature}, "
            f"port={self.app_port}, title='{self.app_title}')"
        )
