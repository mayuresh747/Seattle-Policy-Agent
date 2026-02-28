import os
import pytest
from src.chat_agent.config import get_config, load_config

def test_load_config_success(monkeypatch):
    """Test that configuration loads successfully from the YAML file."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    
    config = get_config()
    
    # Check attributes of the _Config object returned by get_config()
    assert config.app_title == "Seattle Regulatory Friction Observatory"
    assert config.llm_model == "gpt-5.1"
    assert config.llm_temperature == 0.1
    assert config.llm_max_tokens == 4096

def test_config_missing_api_key(monkeypatch):
    """Test that loading config handles API key gracefully."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    
    # The config.py doesn't validate API Keys explicitly upon load, 
    # it just sets OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", ""). 
    # Let's ensure it doesn't crash.
    config = get_config()
    assert getattr(config, "llm_model", None) is not None

