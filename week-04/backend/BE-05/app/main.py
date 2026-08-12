"""
BE-05: Auth & Protected Routes API (Supabase Auth)

A secure RESTful API built with Python 3.10+ and FastAPI, integrated with
Supabase Auth for sign up, log in, log out, JWT token verification, and route protection.

Author: John Elvin Endrenal
Week: 4 (BE-05)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import SUPABASE_URL, PORT
from app.supabase_client import get_supabase_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager logging server startup and connecting to Supabase client."""
    try:
        client = get_supabase_client()
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
    """Return 400 Bad Request for request validation failures."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Bad Request: Missing or invalid payload fields"},
    )


@app.get("/", summary="API Root", description="Returns API metadata and operational status.")
def get_root():
    """Root endpoint describing the API."""
    return {
        "name": "Auth & Protect API",
        "version": "1.0.0",
        "status": "online",
        "supabase_url": SUPABASE_URL,
    }
