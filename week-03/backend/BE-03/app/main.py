"""
BE-03: SQLite-backed CRUD API for Managing a To-Do List

A FastAPI application that connects to a real SQLite database (tasks.db)
for persistent storage, preserving exact RESTful contracts and HTTP status codes.

Author: John Elvin Endrenal
Week: 3 (BE-03)
"""

from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import get_db_connection, init_db, row_to_dict

app = FastAPI(
    title="Task API (SQLite)",
    version="2.0",
    description="A SQLite-backed CRUD API for managing a to-do list built with FastAPI.",
)


@app.on_event("startup")
def startup_event():
    """Initialize database and seed initial data on application startup."""
    init_db()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return 400 Bad Request for validation failures."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Invalid request payload: title is required and cannot be empty"},
    )


@app.get("/", summary="API Root", description="Returns information about the SQLite-backed Task API.")
def get_root():
    """Root endpoint describing the Task API."""
    return {
        "name": "Task API (SQLite)",
        "version": "2.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health", summary="Health Check", description="Health check endpoint to verify server status.")
def get_health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/tasks", summary="List All Tasks", description="Returns all tasks from SQLite database. Supports optional status filtering, keyword search, and alphabetical sorting.")
def get_tasks(
    done: Optional[bool] = None,
    search: Optional[str] = None,
    sort: Optional[str] = None,
):
    """Retrieve all tasks from SQLite with optional filtering and sorting."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if done is not None:
        query += " AND done = ?"
        params.append(1 if done else 0)

    if search is not None and search.strip():
        query += " AND title LIKE ?"
        params.append(f"%{search.strip()}%")

    if sort == "title":
        query += " ORDER BY title ASC"
    else:
        query += " ORDER BY id ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [row_to_dict(row) for row in rows]


@app.get("/tasks/{task_id}", summary="Get Task by ID", description="Returns a single task matching the given ID from SQLite.")
def get_task(task_id: int):
    """Retrieve a single task by ID using a parameterized SQL query."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Task {task_id} not found"},
        )

    return row_to_dict(row)


@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Create Task", description="Inserts a new task into SQLite with parameterized SQL.")
def create_task(payload: dict):
    """Create a new task in SQLite database."""
    if not isinstance(payload, dict) or "title" not in payload:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Title is required"},
        )

    title = payload.get("title")
    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Title cannot be empty"},
        )

    done_val = 1 if bool(payload.get("done", False)) else 0
    clean_title = title.strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (clean_title, done_val),
    )
    conn.commit()

    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (new_id,))
    new_row = cursor.fetchone()
    conn.close()

    return row_to_dict(new_row)


@app.put("/tasks/{task_id}", summary="Update Task", description="Updates a task's title and/or completion status in SQLite.")
def update_task(task_id: int, payload: dict):
    """Update an existing task in SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    existing = cursor.fetchone()

    if existing is None:
        conn.close()
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Task {task_id} not found"},
        )

    if not isinstance(payload, dict) or not payload:
        conn.close()
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Request body cannot be empty"},
        )

    current_title = existing["title"]
    current_done = existing["done"]

    if "title" in payload:
        new_title = payload["title"]
        if not isinstance(new_title, str) or not new_title.strip():
            conn.close()
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Title cannot be empty"},
            )
        current_title = new_title.strip()

    if "done" in payload:
        current_done = 1 if bool(payload["done"]) else 0

    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (current_title, current_done, task_id),
    )
    conn.commit()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    updated_row = cursor.fetchone()
    conn.close()

    return row_to_dict(updated_row)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Task", description="Deletes a task by ID from SQLite.")
def delete_task(task_id: int):
    """Delete a task from SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    existing = cursor.fetchone()

    if existing is None:
        conn.close()
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Task {task_id} not found"},
        )

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/stats", summary="Get Task Statistics", description="Returns aggregate task counts using SQL COUNT().")
def get_stats():
    """Get aggregated statistics directly from SQLite using SQL COUNT()."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM tasks")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = 1")
    done_count = cursor.fetchone()[0]

    conn.close()
    open_count = total - done_count

    return {
        "total": total,
        "done": done_count,
        "open": open_count,
    }


@app.post("/reset", summary="Reset Tasks", description="Resets SQLite database back to initial seed tasks.")
def reset_tasks():
    """Reset SQLite tasks table and re-seed data."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks")
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

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    conn.close()

    return {"message": "Database reset to initial state", "count": count}
