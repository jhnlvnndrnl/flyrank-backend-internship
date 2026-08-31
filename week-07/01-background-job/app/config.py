"""Application Configuration."""

import os
from dotenv import load_dotenv

load_dotenv()

APP_ENV: str = os.getenv("APP_ENV", "development")
PORT: int = int(os.getenv("PORT", "8000"))
INNGEST_DEV: bool = os.getenv("INNGEST_DEV", "true").lower() in ("true", "1", "yes")
INNGEST_EVENT_KEY: str | None = os.getenv("INNGEST_EVENT_KEY")
INNGEST_SIGNING_KEY: str | None = os.getenv("INNGEST_SIGNING_KEY")
