"""
BE-05 Environment Configuration Module

Loads and validates configuration settings from .env file or environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://demo-project.supabase.co")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "demo-anon-key")
PORT: int = int(os.getenv("PORT", "8000"))
