"""In-memory data store for report jobs."""

import datetime
from typing import Any

# In-memory dictionary for storing reports
# Key: report_id (str), Value: report metadata dict
_reports_store: dict[str, dict[str, Any]] = {}


def save_report(report_id: str, topic: str, status: str = "pending") -> dict[str, Any]:
    """Initialize or save a report in memory."""
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    record = {
        "id": report_id,
        "topic": topic,
        "status": status,
        "result": None,
        "error": None,
        "created_at": now,
        "updated_at": now,
    }
    _reports_store[report_id] = record
    return record


def update_report(
    report_id: str,
    status: str,
    result: str | None = None,
    error: str | None = None,
) -> dict[str, Any] | None:
    """Update status, result, and timestamp for an existing report."""
    if report_id not in _reports_store:
        return None

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    _reports_store[report_id]["status"] = status
    _reports_store[report_id]["updated_at"] = now

    if result is not None:
        _reports_store[report_id]["result"] = result
    if error is not None:
        _reports_store[report_id]["error"] = error

    return _reports_store[report_id]


def get_report(report_id: str) -> dict[str, Any] | None:
    """Fetch a single report by ID."""
    return _reports_store.get(report_id)


def get_all_reports() -> list[dict[str, Any]]:
    """Retrieve all reports in storage."""
    return list(_reports_store.values())


def get_summary() -> dict[str, int]:
    """Calculate summary counts by status."""
    summary = {"pending": 0, "done": 0, "failed": 0, "total": len(_reports_store)}
    for r in _reports_store.values():
        st = r.get("status", "pending")
        if st in summary:
            summary[st] += 1
        else:
            summary[st] = 1
    return summary


def reset_store() -> None:
    """Clear in-memory store (primarily for tests)."""
    _reports_store.clear()
