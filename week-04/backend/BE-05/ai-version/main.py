"""
AI-Version: Standalone Auth & Protection API (AI Rematch Quarantine Code)

Generated implementation of the secure Supabase Auth API created by AI prompt.
"""

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel
import os
from supabase import create_client, Client

app = FastAPI(title="AI Auth API")

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://demo-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "demo-key")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class AuthModel(BaseModel):
    email: str
    password: str


@app.post("/auth/signup")
def signup(data: AuthModel):
    res = supabase.auth.sign_up({"email": data.email, "password": data.password})
    return res.user


@app.post("/auth/login")
def login(data: AuthModel):
    res = supabase.auth.sign_in_with_password({"email": data.email, "password": data.password})
    return {"access_token": res.session.access_token}


@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.get("/protected/profile")
def profile(authorization: str = Header(None)):
    token = authorization.split(" ")[1]  # Naive split without checking prefix or empty header
    user = supabase.auth.get_user(token)
    return user.user


@app.post("/auth/logout")
def logout():
    supabase.auth.sign_out()
    return {"message": "logged out"}
