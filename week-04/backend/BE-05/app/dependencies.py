"""
BE-05 Authentication and Authorization Dependencies

Provides reusable FastAPI security dependencies for extracting, verifying,
and validating Supabase JWT access tokens across protected routes.
"""

from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.supabase_client import get_supabase_client

# Define HTTP Bearer security scheme for Swagger UI & OpenAPI specs
security_scheme = HTTPBearer(bearerFormat="JWT", auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> Dict[str, Any]:
    """
    Reusable FastAPI dependency (middleware guard).
    Extracts Bearer token, verifies signature and validity via Supabase Auth,
    and returns verified user details or raises HTTP 401 Unauthorized exception.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Access token required"},
        )

    token = credentials.credentials
    supabase = get_supabase_client()
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid or expired token"},
            )

        user = user_response.user
        return {
            "id": user.id,
            "email": user.email,
            "created_at": str(user.created_at),
            "app_metadata": user.app_metadata or {},
            "user_metadata": user.user_metadata or {},
            "raw_token": token,
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid or expired token"},
        )


async def get_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Authorization guard verifying if user possesses admin role.
    Raises HTTP 403 Forbidden if user is authenticated but lacks admin privileges.
    """
    role = current_user.get("app_metadata", {}).get("role") or current_user.get("user_metadata", {}).get("role")
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Forbidden: Admin privileges required"},
        )
    return current_user
