"""
BE-05 Pytest Suite: Auth & Protected Routes API
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify root endpoint returns API metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Auth & Protect API"
    assert "status" in data


def test_public_info_endpoint():
    """Verify open public endpoint returns HTTP 200 OK without authentication."""
    response = client.get("/public/info")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome stranger! This info is public."}


def test_signup_validation_missing_fields():
    """Verify signup endpoint returns HTTP 400 Bad Request when credentials are missing."""
    response = client.post("/auth/signup", json={"email": "incomplete@example.com"})
    assert response.status_code == 400
    assert response.json() == {"error": "Email and password are required"}


def test_login_validation_missing_fields():
    """Verify login endpoint returns HTTP 400 Bad Request when credentials are missing."""
    response = client.post("/auth/login", json={"password": "password123"})
    assert response.status_code == 400
    assert response.json() == {"error": "Email and password are required"}


def test_login_invalid_credentials():
    """Verify login endpoint returns HTTP 401 Unauthorized for invalid credentials."""
    response = client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword123"},
    )
    assert response.status_code == 401
    assert response.json() == {"error": "Invalid login credentials"}


def test_protected_profile_unauthenticated():
    """Verify protected profile endpoint returns HTTP 401 when Authorization header is missing."""
    response = client.get("/protected/profile")
    assert response.status_code == 401
    assert response.json() == {"error": "Access token required"}


def test_protected_dashboard_unauthenticated():
    """Verify protected dashboard endpoint returns HTTP 401 when Authorization header is missing."""
    response = client.get("/protected/dashboard")
    assert response.status_code == 401
    assert response.json() == {"error": "Access token required"}


def test_protected_profile_tampered_token():
    """Verify protected profile endpoint rejects tampered/invalid Bearer tokens with HTTP 401."""
    response = client.get(
        "/protected/profile",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.tampered.token"},
    )
    assert response.status_code == 401
    assert response.json() == {"error": "Invalid or expired token"}


def test_logout_unauthenticated():
    """Verify logout endpoint returns HTTP 401 when unauthenticated."""
    response = client.post("/auth/logout")
    assert response.status_code == 401
    assert response.json() == {"error": "Access token required"}


def test_admin_stats_unauthenticated():
    """Verify admin endpoint returns HTTP 401 when unauthenticated."""
    response = client.get("/admin/stats")
    assert response.status_code == 401
    assert response.json() == {"error": "Access token required"}


def test_refresh_token_invalid():
    """Verify token refresh endpoint returns HTTP 401 for invalid refresh token."""
    response = client.post("/auth/refresh", json={"refresh_token": "invalid_refresh_token"})
    assert response.status_code == 401
    assert response.json() == {"error": "Invalid or expired refresh token"}
