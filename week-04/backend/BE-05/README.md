# BE-05: Auth · Login & Protect API (Supabase Auth)

A production-grade, secure RESTful API built with **Python 3.10+** and **FastAPI**, integrated with **Supabase Auth** as the Identity Provider. This project implements user authentication (Sign Up, Log In, Log Out, Token Refresh), JWT token verification, reusable middleware guards, and interactive Swagger UI authorization.

---

## Quickstart

### 1. Environment Setup
Copy `.env.example` to `.env` and fill in your Supabase project credentials:
```bash
cp .env.example .env
```

Example `.env`:
```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-anon-public-key
PORT=8000
```

> [!NOTE]
> **Supabase Email Confirmation Setting**:
> In your Supabase Dashboard under **Authentication -> Sign In / Providers -> Email**, set **"Confirm email" to OFF** so newly registered accounts can log in immediately during testing.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
Access the server at **[http://localhost:8000](http://localhost:8000)**.  
Access interactive Swagger UI docs at **[http://localhost:8000/docs](http://localhost:8000/docs)**.

---

## API Endpoints Summary

| HTTP Method | Path | Auth Required | Description | Success Status | Error Status |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `GET` | `/` | No | API metadata & operational status | `200 OK` | - |
| `GET` | `/public/info` | No | Open public info endpoint | `200 OK` | - |
| `POST` | `/auth/signup` | No | Register new user account | `201 Created` | `400 Bad Request` |
| `POST` | `/auth/login` | No | Authenticate credentials & return JWT | `200 OK` | `400 Bad Request`, `401 Unauthorized` |
| `POST` | `/auth/logout` | **Yes (Bearer)** | Sign out user session | `204 No Content` | `401 Unauthorized` |
| `POST` | `/auth/refresh` | No | Exchange refresh token for fresh access token | `200 OK` | `401 Unauthorized` |
| `GET` | `/protected/profile` | **Yes (Bearer)** | Fetch authenticated user profile & metadata | `200 OK` | `401 Unauthorized` |
| `GET` | `/protected/dashboard` | **Yes (Bearer)** | Fetch protected user dashboard metrics | `200 OK` | `401 Unauthorized` |
| `GET` | `/admin/stats` | **Yes (Admin)** | Admin-only stats endpoint (authorization test) | `200 OK` | `401 Unauthorized`, `403 Forbidden` |

---

## 401 vs 403 Status Code Distinction

- **`401 Unauthorized` ("I don't know who you are")**: Returned when authentication token is missing, malformed, invalid, or expired.
  - *Example*: Calling `GET /protected/profile` without an `Authorization: Bearer <token>` header returns `401` (`{"error": "Access token required"}`).
- **`403 Forbidden` ("I know who you are, but you are not allowed")**: Returned when a caller is properly authenticated, but lacks necessary role/permission scopes.
  - *Example*: A authenticated non-admin user calling `GET /admin/stats` returns `403` (`{"error": "Forbidden: Admin privileges required"}`).

---

## Interactive OpenAPI / Swagger UI (`/docs`)

FastAPI serves interactive OpenAPI documentation at `/docs`.

1. Open **[http://localhost:8000/docs](http://localhost:8000/docs)**.
2. Protected endpoints display a **lock icon** 🔒 next to their path.
3. Click the green **Authorize** button at the top right.
4. Enter your JWT `access_token` returned by `POST /auth/login` into the Bearer input field and click **Authorize**.
5. Test protected endpoints (`/protected/profile`, `/protected/dashboard`, `/auth/logout`) directly from your browser with **"Try it out"**.

---

## Automated Testing

Execute the unit test suite with `pytest`:
```bash
PYTHONPATH=. python3 -m pytest -v tests/test_auth.py
```
All 11 unit tests verify input validation, token extraction, 401 error payloads, and endpoint protection.

---

## Verification Commands (`curl`)

```bash
# 1. Public endpoint (200 OK)
curl -i http://localhost:8000/public/info

# 2. Sign up new account (201 Created)
curl -i -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"password123"}'

# 3. Log in to get access token (200 OK)
curl -i -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"password123"}'

# 4. Access protected profile without token (401 Unauthorized)
curl -i http://localhost:8000/protected/profile

# 5. Access protected profile with token (200 OK)
curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"

# 6. Log out session (204 No Content)
curl -i -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

---

## Stage 7: AI vs Me (AI Rematch)

### AI Benchmark Prompt
> "Build a secure RESTful API using FastAPI and Supabase Auth with five endpoints (`POST /auth/signup`, `POST /auth/login`, `POST /auth/logout`, `GET /public/info`, `GET /protected/profile`). Return 201 for signup, 200 for login/reads, 204 for logout, 400 for bad input, and 401 for unauthorized access. Verify tokens via middleware guard and configure OpenAPI HTTPBearer security."

---

### Comparative Evaluation Matrix

| Evaluated Dimension | Hand-Crafted Code (Stages 0–6) | AI Quarantine Code (`ai-version/`) |
| :--- | :--- | :--- |
| **Token Extraction & Parsing** | Checks `Authorization` header presence, validates `Bearer ` prefix explicitly, handles missing/empty tokens cleanly returning status 401. | Naively calls `authorization.split(" ")[1]`, which crashes with an unhandled `AttributeError` or `IndexError` when `Authorization` header is missing or malformed. |
| **Error Handling & Security Flaws** | Catches Supabase SDK exceptions and returns uniform `401 Unauthorized` JSON errors (`{"error": "Invalid or expired token"}`). | Trusts `supabase.auth.get_user(token)` without checking exceptions or return null states, potentially crashing or leaking 500 server stack traces. |
| **Response Specifications** | Strictly returns `204 No Content` for logout, explicit HTTP status codes (`201`, `200`, `400`, `401`, `403`), and custom validation JSON error payloads. | Returned HTTP `200` for logout instead of `204 No Content`, used default FastAPI 422 Unprocessable Entity error payloads instead of explicit 400 Bad Request `{"error": "..."}` payloads. |
| **OpenAPI / Swagger Integration** | Configured `HTTPBearer(bearerFormat="JWT")` dependency attached to protected routes, enabling the Swagger UI `Authorize` padlock. | Left Swagger UI unconfigured without security scheme definitions, making protected endpoints impossible to test directly from `/docs`. |

---

### AI Rematch Reflection Answers

1. **How did it handle token extraction?**
   The AI code used `authorization.split(" ")[1]` without checking if the `Authorization` header was `None`, missing, or properly formatted. Passing no header or a raw token without `Bearer ` causes a 500 Internal Server Error crash rather than returning a proper `401 Unauthorized`.

2. **What security flaws might it have introduced?**
   The AI code failed to catch invalid token exceptions from `supabase.auth.get_user(token)`, exposing raw internal stack traces to callers when an invalid or expired token is passed. Additionally, it did not implement role authorization checks, making HTTP `403 Forbidden` protection impossible.

3. **What did your prompt forget to specify — and what did the AI decide?**
   The prompt forgot to specify exact exception handling for missing headers and custom Pydantic validation handlers. The AI silently decided to rely on FastAPI's default 422 error handlers and generic 500 unhandled exception handling.

4. **One Rematch Lesson**:
   *Adding explicit constraints for header validation, status code contracts (204 vs 200), and OpenAPI security schemes transforms AI-generated code from an unstable prototype into a robust production implementation.*

