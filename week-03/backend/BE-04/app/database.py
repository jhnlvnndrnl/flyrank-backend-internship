"""
Database module for PostgreSQL in BE-04.
Handles connections and table initialization via DATABASE_URL environment variable.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, List
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def get_database_url() -> str:
    """Retrieve and format PostgreSQL DATABASE_URL from environment."""
    url = os.getenv("DATABASE_URL", "postgres://postgres:dev@localhost:5432/tasks")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def get_db_connection():
    """Establish and return a connection to PostgreSQL."""
    conn = psycopg2.connect(get_database_url(), cursor_factory=RealDictCursor)
    return conn


def init_db() -> None:
    """Initialize PostgreSQL tasks table and seed data if table is empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create tasks table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT FALSE
        );
        """
    )

    # Check task count
    cursor.execute("SELECT COUNT(*) AS count FROM tasks;")
    row = cursor.fetchone()
    count = row["count"] if row else 0

    # Seed 3 initial tasks if table is empty
    if count == 0:
        cursor.execute(
            """
            INSERT INTO tasks (title, done) VALUES
            (%s, %s),
            (%s, %s),
            (%s, %s);
            """,
            (
                "Setup development environment", True,
                "Read FastAPI & Postgres documentation", False,
                "Containerize app with Docker Compose", False,
            ),
        )

    conn.commit()
    cursor.close()
    conn.close()


def row_to_dict(row: dict) -> Dict[str, Any]:
    """Convert PostgreSQL RealDictRow to dictionary with boolean 'done'."""
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }
