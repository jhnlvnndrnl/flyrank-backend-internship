"""
BE-05 Pydantic Schemas for Auth Request/Response Models
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


class AuthCredentials(BaseModel):
    """Sign up and Log in request schema."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str = Field(..., min_length=1, description="Refresh token string")


class TokenResponse(BaseModel):
    """Successful authentication token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = 3600
    user: Dict[str, Any]
