"""
BE-04: Containerized PostgreSQL CRUD API for Managing a To-Do List

A FastAPI application that connects to a PostgreSQL database via DATABASE_URL,
designed to run seamlessly both locally and inside Docker Compose containers.

Author: John Elvin Endrenal
Week: 3 (BE-04)
"""

from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import get_db_connection, init_db, row_to_dict

app = FastAPI(
    title="Task API (PostgreSQL)",
    version="3.0",
    description="A containerized PostgreSQL-backed CRUD API built with FastAPI.",
)


@app.on_event("startup")
def startup_event():
    """Initialize database schema and seed data on app startup."""
    try:
        init_db()
    except Exception as e:
        print(f"Warning: Database initialization postponed (waiting for container DB): {e}")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return 400 Bad Request for validation failures."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Invalid request payload: title is required and cannot be empty"},
    )


@app.get("/", summary="API Root", description="Returns information about the PostgreSQL Task API.")
def get_root():
    """Root endpoint describing the Task API."""
    return {
        "name": "Task API (PostgreSQL)",
        "version": "3.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health", summary="Health Check", description="Health check endpoint verifying server and Postgres connectivity.")
def get_health():
    """Health check verifying database connection."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return {"status": "ok", "db": "ok"}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "db": str(e)},
        )


@app.get("/tasks", summary="List All Tasks", description="Returns all tasks from PostgreSQL. Supports status filtering, keyword search, and sorting.")
def get_tasks(
    done: Optional[bool] = None,
    search: Optional[str] = None,
    sort: Optional[str] = None,
):
    """Retrieve all tasks from PostgreSQL with optional filtering."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if done is not None:
        query += " AND done = %s"
        params.append(done)

    if search is not None and search.strip():
        query += " AND title ILIKE %s"
        params.append(f"%{search.strip()}%")

    if sort == "title":
        query += " ORDER BY title ASC"
    else:
        query += " ORDER BY id ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [row_to_dict(row) for row in rows]


@app.get("/tasks/{task_id}", summary="Get Task by ID", description="Returns a single task matching ID using parameterized SQL.")
def get_task(task_id: int):
    """Retrieve a single task by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = %s;", (task_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Task {task_id} not found"},
        )

    return row_to_dict(row)


@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Create Task", description="Inserts a new task into PostgreSQL.")
def create_task(payload: dict):
    """Create a new task in PostgreSQL."""
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

    done_val = bool(payload.get("done", False))
    clean_title = title.strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *;",
        (clean_title, done_val),
    )
    new_row = cursor.fetchone()
    conn.commit()

    cursor.close()
    conn.close()

    return row_to_dict(new_row)


@app.put("/tasks/{task_id}", summary="Update Task", description="Updates a task's title/completion status in PostgreSQL.")
def update_task(task_id: int, payload: dict):
    """Update an existing task in PostgreSQL."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = %s;", (task_id,))
    existing = cursor.fetchone()

    if existing is None:
        cursor.close()
        conn.close()
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Task {task_id} not found"},
        )

    if not isinstance(payload, dict) or not payload:
        cursor.close()
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
            cursor.close()
            conn.close()
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Title cannot be empty"},
            )
        current_title = new_title.strip()

    if "done" in payload:
        current_done = bool(payload["done"])

    cursor.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *;",
        (current_title, current_done, task_id),
    )
    updated_row = cursor.fetchone()
    conn.commit()

    cursor.close()
    conn.close()

    return row_to_dict(updated_row)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Task", description="Deletes a task by ID from PostgreSQL.")
def delete_task(task_id: int):
    """Delete a task from PostgreSQL."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = %s;", (task_id,))
    existing = cursor.fetchone()

    if existing is None:
        cursor.close()
        conn.close()
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Task {task_id} not found"},
        )

    cursor.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/stats", summary="Get Task Statistics", description="Returns aggregate task metrics from PostgreSQL.")
def get_stats():
    """Get aggregate statistics using SQL COUNT()."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total, COUNT(*) FILTER (WHERE done = true) AS done_count FROM tasks;")
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    total = row["total"] if row else 0
    done_count = row["done_count"] if row else 0
    open_count = total - done_count

    return {
        "total": total,
        "done": done_count,
        "open": open_count,
    }


@app.post("/reset", summary="Reset Tasks", description="Resets PostgreSQL tasks table to initial seed state.")
def reset_tasks():
    """Reset tasks table in PostgreSQL."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("TRUNCATE TABLE tasks RESTART IDENTITY;")
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

    cursor.execute("SELECT COUNT(*) AS count FROM tasks;")
    count = cursor.fetchone()["count"]

    cursor.close()
    conn.close()

    return {"message": "Database reset to initial state", "count": count}
