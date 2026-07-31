"""
BE-02: CRUD API for Managing a To-Do List

A FastAPI application that implements a complete CRUD (Create, Read, Update, Delete)
API for managing tasks stored in memory.

Author: John Elvin Endrenal
Week: 2 (BE-02)
"""

from typing import Optional
from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A CRUD API for managing a to-do list built with FastAPI.",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return 400 Bad Request for validation failures."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Invalid request payload: title is required and cannot be empty"},
    )


# Initial seed data for in-memory tasks
SEED_TASKS = [
    {"id": 1, "title": "Setup development environment", "done": True},
    {"id": 2, "title": "Read FastAPI documentation", "done": False},
    {"id": 3, "title": "Build CRUD endpoints", "done": False},
]

# In-memory task list
tasks = [dict(t) for t in SEED_TASKS]


@app.get("/", summary="API Root", description="Returns information about the API and available endpoints.")
def get_root():
    """Root endpoint describing the Task API."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health", summary="Health Check", description="Health check endpoint to verify server status.")
def get_health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/tasks", summary="List All Tasks", description="Returns a list of all tasks. Supports optional filtering by completion status (done) and keyword search.")
def get_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    """Retrieve all tasks with optional filtering and search."""
    result = tasks
    if done is not None:
        result = [t for t in result if t["done"] == done]
    if search is not None and search.strip():
        query = search.strip().lower()
        result = [t for t in result if query in t["title"].lower()]
    return result


@app.get("/tasks/{task_id}", summary="Get Task by ID", description="Returns a single task matching the given ID.")
def get_task(task_id: int):
    """Retrieve a single task by ID."""
    for task in tasks:
        if task["id"] == task_id:
            return task
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": f"Task {task_id} not found"},
    )


@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Create Task", description="Creates a new task with the provided title.")
def create_task(payload: dict):
    """Create a new task."""
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

    done = bool(payload.get("done", False))
    next_id = max([t["id"] for t in tasks], default=0) + 1

    new_task = {
        "id": next_id,
        "title": title.strip(),
        "done": done,
    }
    tasks.append(new_task)
    return new_task


@app.put("/tasks/{task_id}", summary="Update Task", description="Updates a task's title and/or completion status.")
def update_task(task_id: int, payload: dict):
    """Update an existing task by ID."""
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Task {task_id} not found"},
        )

    if not isinstance(payload, dict) or not payload:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Request body cannot be empty"},
        )

    if "title" in payload:
        title = payload["title"]
        if not isinstance(title, str) or not title.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Title cannot be empty"},
            )
        task["title"] = title.strip()

    if "done" in payload:
        task["done"] = bool(payload["done"])

    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Task", description="Deletes a task by ID.")
def delete_task(task_id: int):
    """Delete a task by ID."""
    global tasks
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Task {task_id} not found"},
        )

    tasks = [t for t in tasks if t["id"] != task_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/stats", summary="Get Task Statistics", description="Returns total, completed, and open task counts.")
def get_stats():
    """Get aggregated statistics for tasks."""
    total = len(tasks)
    done_count = len([t for t in tasks if t["done"]])
    open_count = total - done_count
    return {
        "total": total,
        "done": done_count,
        "open": open_count,
    }


@app.post("/reset", summary="Reset Tasks", description="Resets the in-memory task database back to initial seed data.")
def reset_tasks():
    """Reset task database to initial seed data."""
    global tasks
    tasks = [dict(t) for t in SEED_TASKS]
    return {"message": "Tasks reset to initial state", "count": len(tasks)}