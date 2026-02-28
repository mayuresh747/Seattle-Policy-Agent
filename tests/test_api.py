import pytest
from fastapi.testclient import TestClient
import os

# Set environment variable before importing main so the app loads correctly
os.environ["OPENAI_API_KEY"] = "test-key-123"

from src.chat_agent.main import app

client = TestClient(app)

def test_read_main():
    """Test that the index root serves the HTML file."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_get_config():
    """Test that the /api/config endpoint returns the correct sanitized config."""
    response = client.get("/api/config")
    assert response.status_code == 200
    
    data = response.json()
    assert "title" in data
    assert "subtitle" in data
    assert "example_queries" in data
    assert "system_prompt" not in data  # Ensure system prompt isn't leaked
    
    assert data["title"] == "Seattle Regulatory Friction Observatory"

def test_clear_history():
    """Test clearing chat history endpoint."""
    response = client.delete("/api/chat/history", params={"session_id": "test-session-123"})
    assert response.status_code == 200
    assert response.json()["message"] == "Conversation cleared"

def test_get_settings():
    """Test the /api/settings endpoint."""
    response = client.get("/api/settings", params={"session_id": "test-session-123"})
    assert response.status_code == 200
    
    data = response.json()
    assert "system_prompt" in data
    assert "temperature" in data
    assert data["temperature"] == 0.1

