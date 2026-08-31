"""Configuration settings for PDF Report Generator."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

APP_ENV: str = os.getenv("APP_ENV", "development")
PORT: int = int(os.getenv("PORT", "8000"))
DATABASE_PATH: str = os.getenv("DATABASE_PATH", str(BASE_DIR / "report.db"))
REPORTS_DIR: str = os.getenv("REPORTS_DIR", str(BASE_DIR / "reports"))

os.makedirs(REPORTS_DIR, exist_ok=True)
