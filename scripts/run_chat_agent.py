"""
Launch script for the Chat Agent server.
Run:  python scripts/run_chat_agent.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from src.chat_agent.config import get_config


def main():
    cfg = get_config()
    print(f"\n  🚀 {cfg.app_title}")
    print(f"     {cfg.app_subtitle}")
    print(f"     Model: {cfg.llm_model}  |  Temp: {cfg.llm_temperature}")
    print(f"     http://localhost:{cfg.app_port}\n")

    uvicorn.run(
        "src.chat_agent.main:app",
        host="0.0.0.0",
        port=cfg.app_port,
        reload=True,
    )


if __name__ == "__main__":
    main()
