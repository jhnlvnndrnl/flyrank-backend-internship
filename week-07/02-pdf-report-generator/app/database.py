"""SQLite Database initialization and helpers."""

import sqlite3
from typing import Any
from .config import DATABASE_PATH


def get_connection(db_path: str = DATABASE_PATH) -> sqlite3.Connection:
    """Create and return a SQLite connection configured with Row factory."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DATABASE_PATH) -> None:
    """Initialize database tables for orders and reports."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # Orders Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer TEXT NOT NULL,
                product TEXT NOT NULL,
                amount REAL NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )

        # Reports Metadata Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                report_date TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.commit()


def save_report_meta(report_id: str, path: str, report_date: str, created_at: str, db_path: str = DATABASE_PATH) -> dict[str, Any]:
    """Insert a generated report record into the database."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO reports (id, path, report_date, created_at)
            VALUES (?, ?, ?, ?);
            """,
            (report_id, path, report_date, created_at),
        )
        conn.commit()
    return {
        "id": report_id,
        "path": path,
        "report_date": report_date,
        "created_at": created_at,
    }


def get_report_by_id(report_id: str, db_path: str = DATABASE_PATH) -> dict[str, Any] | None:
    """Retrieve report metadata by ID."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, path, report_date, created_at FROM reports WHERE id = ?;", (report_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_today_report(report_date: str, db_path: str = DATABASE_PATH) -> dict[str, Any] | None:
    """Fetch existing report generated for a specific date (for idempotency check)."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, path, report_date, created_at FROM reports WHERE report_date = ? ORDER BY created_at DESC LIMIT 1;", (report_date,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_all_reports(db_path: str = DATABASE_PATH) -> list[dict[str, Any]]:
    """List all generated reports."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, path, report_date, created_at FROM reports ORDER BY created_at DESC;")
        return [dict(row) for row in cursor.fetchall()]
