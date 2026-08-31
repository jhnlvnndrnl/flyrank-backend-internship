"""FastAPI Application for Background Job API."""

import uuid
from typing import Any
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import inngest
import inngest.fast_api

from .inngest_client import inngest_client
from .functions import say_hello, make_report, heartbeat
from .storage import save_report, get_report, get_all_reports, get_summary

app = FastAPI(
    title="Report Background Job API",
    description="FastAPI + Inngest asynchronous job orchestration with retries, polling, and cron heartbeat.",
    version="1.0.0",
)


# Request schemas
class CreateReportRequest(BaseModel):
    topic: str = Field(..., description="Report topic name")


# Stage 0: Hello Server
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


# Stage 2 & 3: Fast door - Accept now, work later
@app.post("/reports", status_code=status.HTTP_202_ACCEPTED, tags=["Reports"])
async def create_report(payload: dict[str, Any]) -> JSONResponse:
    """
    Accept report creation request immediately with HTTP 202 Accepted.
    Rejects invalid/missing topic with HTTP 400 without triggering background jobs.
    """
    topic = payload.get("topic") if isinstance(payload, dict) else None

    # Input validation: reject at the door
    if not topic or not isinstance(topic, str) or not topic.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Topic is required and cannot be empty."},
        )

    topic = topic.strip()
    report_id = f"rep_{uuid.uuid4().hex[:10]}"

    # Save initial pending state in-memory
    record = save_report(report_id=report_id, topic=topic, status="pending")

    # Send event to Inngest for asynchronous background execution
    try:
        await inngest_client.send(
            inngest.Event(
                name="report/requested",
                data={"id": report_id, "topic": topic},
            )
        )
    except Exception:
        # In case Inngest dev server is temporarily offline, the job was accepted
        # and recorded in memory
        pass

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "id": record["id"],
            "topic": record["topic"],
            "status": record["status"],
            "created_at": record["created_at"],
        },
    )


# Stage 2: Status Polling Endpoint
@app.get("/reports/{report_id}", tags=["Reports"])
async def get_report_status(report_id: str) -> dict[str, Any]:
    """
    Status endpoint for polling progress of a background job.
    Transitions from pending -> done / failed.
    """
    report = get_report(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID '{report_id}' not found.",
        )
    return report


# Control Panel (Optional Extras)
@app.get("/reports", tags=["Reports"])
async def list_all_reports() -> dict[str, Any]:
    """List all reports and current summary counts."""
    return {
        "summary": get_summary(),
        "reports": get_all_reports(),
    }


# Trigger manual hello event for testing Stage 1
@app.post("/test/hello", tags=["Testing"])
async def trigger_hello() -> dict[str, str]:
    """Trigger test/hello event to test Inngest worker."""
    await inngest_client.send(inngest.Event(name="test/hello", data={}))
    return {"message": "Event 'test/hello' sent to Inngest."}


# Serve Inngest Functions at /api/inngest
inngest.fast_api.serve(
    app,
    inngest_client,
    [say_hello, make_report, heartbeat],
    serve_path="/api/inngest",
)
