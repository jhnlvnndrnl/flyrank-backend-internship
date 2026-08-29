"""
BE-07 Environment Configuration Module

Loads and validates configuration settings from .env file or environment variables.
All LLM-related settings live here so the rest of the code never touches os.environ directly.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# --- LLM Provider Configuration ---
# These three variables are the ONLY difference between providers.
# Change them to swap from OpenRouter to Ollama (or any OpenAI-compatible API).
LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
LLM_MODEL: str = os.getenv("LLM_MODEL", "openrouter/auto")

# --- Feature Flags ---
# Stub mode: skip the model entirely, return a hard-coded valid response
LLM_STUB: bool = os.getenv("LLM_STUB", "0") == "1"

# Kill switch: disable LLM calls and return a safe fallback (or 503)
LLM_ENABLED: bool = os.getenv("LLM_ENABLED", "true").lower() == "true"

# --- Server ---
PORT: int = int(os.getenv("PORT", "8000"))

# --- Prompt ---
PROMPT_VERSION: str = "v1"
