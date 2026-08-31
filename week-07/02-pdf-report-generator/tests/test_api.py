"""Automated Tests for PDF Report Generator API."""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from app.config import DATABASE_PATH, REPORTS_DIR
from app.database import init_db, get_connection
from app.queries import get_report_data
from app.renderer import generate_html_report, render_pdf_from_data
from seed import seed_database
from app.main import app

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """Setup test database and seed data."""
    init_db(DATABASE_PATH)
    seed_database(DATABASE_PATH, target_count=200)
    yield


def test_stage_0_health_endpoint():
    """Stage 0: GET /health returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_stage_1_seed_idempotency():
    """Stage 1: Seed script creates exactly 200 rows, and running twice does not duplicate rows."""
    count1 = seed_database(DATABASE_PATH, target_count=200)
    assert count1 == 200

    count2 = seed_database(DATABASE_PATH, target_count=200)
    assert count2 == 200


def test_stage_2_aggregation_queries():
    """Stage 2: get_report_data returns valid metrics, top 5, and daily breakdown."""
    data = get_report_data(DATABASE_PATH)

    metrics = data["metrics"]
    assert metrics["total_orders"] == 200
    assert metrics["total_revenue"] > 0
    assert metrics["avg_order_value"] > 0

    top_products = data["top_products"]
    assert len(top_products) <= 5
    assert len(top_products) > 0
    # Verify top product revenue is <= total revenue
    assert top_products[0]["revenue"] <= metrics["total_revenue"]

    all_orders = data["all_orders"]
    assert len(all_orders) == 200


def test_stage_3_html_generation():
    """Stage 3: HTML template contains required print CSS and tables."""
    data = get_report_data(DATABASE_PATH)
    html = generate_html_report(data)

    assert "table-header-group" in html
    assert "break-inside: avoid" in html
    assert "Top 5 Products" in html
    assert "Master Orders Ledger" in html


@pytest.mark.asyncio
async def test_stage_3_pdf_rendering():
    """Stage 3: Playwright renders valid PDF file on disk."""
    data = get_report_data(DATABASE_PATH)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        pdf_path = await render_pdf_from_data(data, tmp_path)
        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 1000  # Non-empty PDF
        with open(pdf_path, "rb") as f:
            header = f.read(5)
            assert header == b"%PDF-"  # Valid PDF signature
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_stage_4_generate_and_download_flow():
    """Stage 4: POST /reports generates report and GET /reports/:id/file serves it."""
    # Generate with force=True to guarantee new report
    post_res = client.post("/reports", json={"force": True})
    assert post_res.status_code == 201
    data = post_res.json()
    assert "id" in data
    assert "file" in data
    report_id = data["id"]
    file_uri = data["file"]

    # Metadata check
    meta_res = client.get(f"/reports/{report_id}")
    assert meta_res.status_code == 200
    assert meta_res.json()["id"] == report_id

    # Download check
    file_res = client.get(file_uri)
    assert file_res.status_code == 200
    assert file_res.headers["content-type"] == "application/pdf"
    assert len(file_res.content) > 1000
    assert file_res.content[:5] == b"%PDF-"


def test_stage_5_idempotency_same_day():
    """Stage 5: Back-to-back POST requests return the same report ID (idempotent)."""
    res1 = client.post("/reports", json={"force": False})
    res2 = client.post("/reports", json={"force": False})

    data1 = res1.json()
    data2 = res2.json()

    assert data1["id"] == data2["id"]
    assert data1["file"] == data2["file"]
    assert data2["cached"] is True


def test_control_panel_list_reports():
    """Checks GET /reports returns list of generated reports."""
    res = client.get("/reports")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "reports" in data
    assert data["total"] >= 1
