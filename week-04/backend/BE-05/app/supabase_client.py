"""
BE-05 Supabase Client Module

Initializes and manages the Supabase Python SDK Client.
"""

from supabase import create_client, Client
from app.config import SUPABASE_URL, SUPABASE_KEY

_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    """Return an initialized Supabase Client instance."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client
