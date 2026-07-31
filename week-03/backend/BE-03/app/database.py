"""
Database helper module for BE-03 SQLite task manager.
"""

import os
import sqlite3
from typing import Dict, List, Any

# Database file location (stored at week-03/backend/BE-03/tasks.db)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "tasks.db")


def get_db_connection() -> sqlite3.Connection:
    """Establish and return a SQLite database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize database schema and seed initial tasks if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    # Check if table is empty
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    # Seed initial tasks if table is empty
    if count == 0:
        seed_data = [
            ("Setup development environment", 1),
            ("Read FastAPI documentation", 0),
            ("Build CRUD endpoints with SQLite", 0),
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            seed_data,
        )

    conn.commit()
    conn.close()


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert a SQLite Row object to a task dictionary with boolean 'done'."""
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }
