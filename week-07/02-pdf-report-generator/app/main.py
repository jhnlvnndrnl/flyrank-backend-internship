"""FastAPI Application for PDF Report Generator API."""

import datetime
import os
import uuid
from typing import Any
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from contextlib import asynccontextmanager

from .config import DATABASE_PATH, REPORTS_DIR
from .database import (
    init_db,
    save_report_meta,
    get_report_by_id,
    get_today_report,
    get_all_reports,
)
from .queries import get_report_data
from .renderer import render_pdf_from_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and ensure reports directory exists on startup."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    init_db(DATABASE_PATH)
    yield


app = FastAPI(
    title="PDF Report Generator API",
    description="SQL aggregation to automated PDF reports rendered via headless Playwright Chromium and served by link.",
    version="1.0.0",
    lifespan=lifespan,
)


class GenerateReportRequest(BaseModel):
    force: bool = Field(default=False, description="Bypass idempotency cache and regenerate a fresh PDF report.")


# Stage 0: Health Check
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


# Stage 4 & 5: Generate Report Endpoint with Idempotency
@app.post("/reports", tags=["Reports"])
async def generate_report(payload: GenerateReportRequest | None = None) -> JSONResponse:
    """
    Generate sales PDF report from SQLite aggregations.
    Stage 5 Idempotency: Returns existing report if already generated today unless force=true.
    """
    force = payload.force if payload else False
    today_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    # Stage 5 Idempotency Check
    if not force:
        existing_report = get_today_report(today_str, DATABASE_PATH)
        if existing_report and os.path.exists(existing_report["path"]):
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "id": existing_report["id"],
                    "file": f"/reports/{existing_report['id']}/file",
                    "report_date": existing_report["report_date"],
                    "cached": True,
                    "created_at": existing_report["created_at"],
                },
            )

    # Execute 4-step pipeline: Query -> Render -> Store -> Serve
    report_id = f"sales_{today_str}_{uuid.uuid4().hex[:6]}"
    pdf_filename = f"{report_id}.pdf"
    pdf_filepath = os.path.join(REPORTS_DIR, pdf_filename)
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Step 1: Query SQL Aggregations
    data = get_report_data(DATABASE_PATH)

    # Step 2: Render HTML -> PDF via Playwright
    await render_pdf_from_data(data, pdf_filepath)

    # Step 3: Store metadata in DB
    save_report_meta(
        report_id=report_id,
        path=pdf_filepath,
        report_date=today_str,
        created_at=created_at,
        db_path=DATABASE_PATH,
    )

    # Step 4: Hand out the link (HTTP 201 Created)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "id": report_id,
            "file": f"/reports/{report_id}/file",
            "report_date": today_str,
            "cached": False,
            "created_at": created_at,
        },
    )


# Stage 4: Status / Metadata Endpoint
@app.get("/reports/{report_id}", tags=["Reports"])
async def get_report_metadata(report_id: str) -> dict[str, Any]:
    """Retrieve metadata and download link for a given report ID."""
    report = get_report_by_id(report_id, DATABASE_PATH)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID '{report_id}' not found.",
        )
    return {
        "id": report["id"],
        "file": f"/reports/{report['id']}/file",
        "report_date": report["report_date"],
        "created_at": report["created_at"],
    }


# Stage 4: Download / File Serving Endpoint
@app.get("/reports/{report_id}/file", tags=["Reports"])
async def download_report_file(report_id: str) -> FileResponse:
    """Serve the generated PDF file from disk."""
    report = get_report_by_id(report_id, DATABASE_PATH)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID '{report_id}' not found.",
        )

    file_path = report["path"]
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PDF artifact for report '{report_id}' is missing from disk.",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"{report_id}.pdf",
    )


# Optional Extra: Control Panel List All Reports
@app.get("/reports", tags=["Reports"])
async def list_reports() -> dict[str, Any]:
    """Control panel: List all generated reports with direct file links."""
    reports = get_all_reports(DATABASE_PATH)
    return {
        "total": len(reports),
        "reports": [
            {
                "id": r["id"],
                "file": f"/reports/{r['id']}/file",
                "report_date": r["report_date"],
                "created_at": r["created_at"],
            }
            for r in reports
        ],
    }
