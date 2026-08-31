"""Automated tests for Background Job API."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import reset_store, save_report, update_report

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    reset_store()
    yield
    reset_store()


def test_stage_0_health_endpoint():
    """Stage 0: GET /health returns 200 and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_stage_2_post_reports_accepted():
    """Stage 2: POST /reports with valid topic returns 202 Accepted and report ID."""
    response = client.post("/reports", json={"topic": "cats"})
    assert response.status_code == 202
    data = response.json()
    assert "id" in data
    assert data["topic"] == "cats"
    assert data["status"] == "pending"


def test_stage_2_polling_status():
    """Stage 2: GET /reports/:id returns pending first, then done once updated."""
    post_res = client.post("/reports", json={"topic": "dogs"})
    report_id = post_res.json()["id"]

    # Initial state is pending
    get_res = client.get(f"/reports/{report_id}")
    assert get_res.status_code == 200
    assert get_res.json()["status"] == "pending"

    # Simulate worker completion
    update_report(report_id, status="done", result="Analysis of dogs finished")
    done_res = client.get(f"/reports/{report_id}")
    assert done_res.status_code == 200
    assert done_res.json()["status"] == "done"
    assert done_res.json()["result"] == "Analysis of dogs finished"


def test_stage_2_unknown_id_404():
    """Stage 2: GET /reports/unknown_id returns 404 Not Found."""
    response = client.get("/reports/non_existent_123")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_stage_3_missing_topic_returns_400():
    """Stage 3: POST /reports without topic returns 400 Bad Request."""
    response = client.post("/reports", json={})
    assert response.status_code == 400
    assert "error" in response.json()

    # Empty string topic
    response_empty = client.post("/reports", json={"topic": "   "})
    assert response_empty.status_code == 400
    assert "error" in response_empty.json()


def test_control_panel_summary():
    """Tests GET /reports list and summary metrics."""
    client.post("/reports", json={"topic": "topic_a"})
    client.post("/reports", json={"topic": "topic_b"})

    response = client.get("/reports")
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["pending"] == 2
    assert len(data["reports"]) == 2
