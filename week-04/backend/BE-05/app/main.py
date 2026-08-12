"""
BE-05: Auth & Protected Routes API (Supabase Auth)

A secure RESTful API built with Python 3.10+ and FastAPI, integrated with
Supabase Auth for sign up, log in, log out, JWT token verification, and route protection.

Author: John Elvin Endrenal
Week: 4 (BE-05)
"""

from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, Request, Response, status, Body, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import SUPABASE_URL, PORT
from app.supabase_client import get_supabase_client
from app.dependencies import get_current_user, get_admin_user, security_scheme
from app.schemas import RefreshTokenRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager logging server startup and connecting to Supabase client."""
    try:
        get_supabase_client()
        print(f"Server running and connected to Supabase ({SUPABASE_URL}) on port {PORT}")
    except Exception as e:
        print(f"Warning: Supabase client initialization check: {e}")
    yield


app = FastAPI(
    title="Auth & Protect API (Supabase Auth)",
    version="1.0.0",
    description="A secure RESTful API with Supabase Auth integration, JWT verification, and bearer protected routes.",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return 400 Bad Request for request payload validation failures."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Email and password are required"},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Ensure all HTTP exceptions return structured error payloads."""
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        content = exc.detail
    else:
        content = {"error": str(exc.detail)}
    return JSONResponse(status_code=exc.status_code, content=content)


@app.get("/", summary="API Root", description="Returns API metadata and operational status.")
def get_root():
    """Root endpoint describing the API."""
    return {
        "name": "Auth & Protect API",
        "version": "1.0.0",
        "status": "online",
        "supabase_url": SUPABASE_URL,
    }


# ==========================================
# STAGE 1: AUTHENTICATION ENDPOINTS
# ==========================================

@app.post(
    "/auth/signup",
    status_code=status.HTTP_201_CREATED,
    summary="Sign Up New User",
    description="Register a new user account with Supabase Auth.",
)
async def signup(payload: Dict[str, Any] = Body(...)):
    """Create a new user account via Supabase Auth."""
    email = payload.get("email")
    password = payload.get("password")

    if not email or not password or str(email).strip() == "" or str(password).strip() == "":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Email and password are required"},
        )

    supabase = get_supabase_client()
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "User signup failed or user already exists"},
            )

        user_data = {
            "id": response.user.id,
            "email": response.user.email,
            "created_at": str(response.user.created_at),
            "app_metadata": response.user.app_metadata,
            "user_metadata": response.user.user_metadata,
        }
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"user": user_data})
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"Signup failed: {str(exc)}"},
        )


@app.post(
    "/auth/login",
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate credentials with Supabase Auth and receive a JWT access token.",
)
async def login(payload: Dict[str, Any] = Body(...)):
    """Authenticate user credentials and return JWT access token."""
    email = payload.get("email")
    password = payload.get("password")

    if not email or not password or str(email).strip() == "" or str(password).strip() == "":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Email and password are required"},
        )

    supabase = get_supabase_client()
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if not response.session or not response.session.access_token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid login credentials"},
            )

        session = response.session
        user = response.user
        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer",
            "expires_in": session.expires_in,
            "user": {
                "id": user.id if user else None,
                "email": user.email if user else email,
                "created_at": str(user.created_at) if user and user.created_at else None,
            },
        }
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid login credentials"},
        )


@app.post(
    "/auth/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User Logout",
    description="Invalidate session and sign out user via Supabase Auth.",
)
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Sign out user session and return HTTP 204 No Content."""
    supabase = get_supabase_client()
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post(
    "/auth/refresh",
    status_code=status.HTTP_200_OK,
    summary="Refresh Access Token",
    description="Exchange a valid refresh token for a new access token.",
)
async def refresh_token(payload: RefreshTokenRequest):
    """Refresh access token using refresh_token."""
    supabase = get_supabase_client()
    try:
        res = supabase.auth.refresh_session(payload.refresh_token)
        if not res or not res.session:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid or expired refresh token"},
            )
        return {
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token,
            "token_type": "bearer",
            "expires_in": res.session.expires_in,
        }
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid or expired refresh token"},
        )


# ==========================================
# STAGE 2, 3, 4: PUBLIC & PROTECTED ROUTES
# ==========================================

@app.get(
    "/public/info",
    status_code=status.HTTP_200_OK,
    summary="Get Public Information",
    description="Open endpoint reachable by anyone without authentication.",
)
def get_public_info():
    """Public route returning open data."""
    return {"message": "Welcome stranger! This info is public."}


@app.get(
    "/protected/profile",
    status_code=status.HTTP_200_OK,
    summary="Get Protected Profile",
    description="Protected route using reusable FastAPI auth middleware guard.",
)
def get_protected_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Protected profile endpoint returning authenticated user metadata."""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "created_at": current_user["created_at"],
        "app_metadata": current_user["app_metadata"],
        "user_metadata": current_user["user_metadata"],
    }


@app.get(
    "/protected/dashboard",
    status_code=status.HTTP_200_OK,
    summary="Get Protected Dashboard",
    description="Second protected route demonstrating reusable auth middleware guard.",
)
def get_protected_dashboard(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Protected dashboard endpoint demonstrating reusable middleware authorization."""
    return {
        "message": f"Welcome to your private dashboard, {current_user['email']}!",
        "metrics": {
            "audits_completed": 12,
            "seo_score": 94,
            "status": "Active Intern",
        },
    }


@app.get(
    "/admin/stats",
    status_code=status.HTTP_200_OK,
    summary="Get Admin Statistics",
    description="Protected endpoint demonstrating 403 Forbidden authorization failure for non-admins.",
)
def get_admin_stats(admin_user: Dict[str, Any] = Depends(get_admin_user)):
    """Admin-only endpoint returning HTTP 403 when user is authenticated but not an admin."""
    return {
        "admin": admin_user["email"],
        "system_stats": {"total_users": 1500, "active_sessions": 42},
    }
