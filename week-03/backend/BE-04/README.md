# BE-04: Containerized Stack with PostgreSQL & Docker Compose

A production-ready RESTful CRUD API built with **Python 3.10+** and **FastAPI**, connected to a **PostgreSQL** database running in a Docker container, fully orchestrated using **Docker Compose**.

---

## Quickstart (One Command Setup)

### 1. Configure Environment Secrets
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 2. Start the Whole Stack
```bash
docker compose up
```
This single command builds the FastAPI container (`api`) and spins up the PostgreSQL container (`db`). The application automatically initializes the database schema and seeds initial tasks on startup.

Access the API at: **[http://localhost:8000](http://localhost:8000)**  
Access Swagger UI at: **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## Stack Architecture

```text
Host System (localhost:8000)
    │
    ▼
┌──────────────────────────────────────────────┐
│             Docker Compose Network           │
│                                              │
│  ┌─────────────────┐    ┌─────────────────┐  │
│  │   api service   │───►│   db service    │  │
│  │ (FastAPI App)   │    │  (PostgreSQL)   │  │
│  └─────────────────┘    └────────┬────────┘  │
└──────────────────────────────────┼───────────┘
                                   │
                                   ▼
                         Named Volume (taskdata)
```

- **api Service**: FastAPI server exposed on port `8000`. Connects to `db` using `DATABASE_URL=postgres://postgres:dev@db:5432/tasks`.
- **db Service**: Official `postgres:15-alpine` container running on port `5432`.
- **taskdata Volume**: Preserves PostgreSQL database data across `docker compose down` and `docker compose up`.

---

## Environment Secrets (`.env`)

Secrets are isolated from source code using `.env` (git-ignored).

Example `.env.example`:
```env
DATABASE_URL=postgres://postgres:dev@localhost:5432/tasks
```

---

## Parameterized SQL Queries Used

All queries utilize **parameterized placeholders (`%s`)** to prevent SQL injection:

- **Read All / Filter**:
  ```sql
  SELECT * FROM tasks WHERE 1=1 AND done = %s AND title ILIKE %s ORDER BY id ASC;
  ```
- **Read One**:
  ```sql
  SELECT * FROM tasks WHERE id = %s;
  ```
- **Insert**:
  ```sql
  INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *;
  ```
- **Update**:
  ```sql
  UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *;
  ```
- **Delete**:
  ```sql
  DELETE FROM tasks WHERE id = %s;
  ```
- **Stats**:
  ```sql
  SELECT COUNT(*) AS total, COUNT(*) FILTER (WHERE done = true) AS done_count FROM tasks;
  ```

---

## API Endpoints Summary

| CRUD Operation | HTTP Method | Path | Description | Success Code | Error Codes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Root** | `GET` | `/` | API metadata | `200 OK` | - |
| **Health** | `GET` | `/health` | Verifies server and PostgreSQL connection | `200 OK` | `503 Service Unavailable` |
| **Read All** | `GET` | `/tasks` | List tasks (supports `?done=true`, `?search=keyword`, `?sort=title`) | `200 OK` | - |
| **Read One** | `GET` | `/tasks/{id}` | Retrieve a task by ID | `200 OK` | `404 Not Found` |
| **Create** | `POST` | `/tasks` | Insert a new task | `201 Created` | `400 Bad Request` |
| **Update** | `PUT` | `/tasks/{id}` | Update title/completion of a task | `200 OK` | `400 Bad Request`, `404 Not Found` |
| **Delete** | `DELETE` | `/tasks/{id}` | Remove a task by ID | `204 No Content` | `404 Not Found` |
| **Stats** | `GET` | `/stats` | Aggregated statistics via SQL `COUNT()` | `200 OK` | - |
| **Reset** | `POST` | `/reset` | Re-initialize database seed tasks | `200 OK` | - |

---

## Container Database Inspection (`psql`)

Inspect database tables inside the running PostgreSQL container:

```bash
docker exec -it $(docker ps -q -f name=db) psql -U postgres -d tasks
```

Example commands inside `psql`:
```sql
\dt
SELECT * FROM tasks;
\q
```

---

## AI vs Me Section

### Prompt Used:
> "Containerize a FastAPI task CRUD API connecting to PostgreSQL with psycopg2. Create a Dockerfile, compose.yaml with api and db services using a named volume for persistence, and a .env file for DATABASE_URL secrets. Ensure table auto-creation, seed-once rules, parameterized queries with %s, and custom 400 JSON error handling."

### Concrete Differences:
1. **Container Networking**: Hand-crafted `compose.yaml` specifies internal service host routing (`@db:5432/tasks`) inside Docker networks while using `@localhost:5432/tasks` for local development.
2. **PostgreSQL Parameterization**: Hand-crafted version uses proper `%s` tuple parameter binding for `psycopg2` rather than string formatting.
3. **Database Health Endpoint**: `GET /health` tests live database connectivity (`SELECT 1;`) returning `503 Service Unavailable` if database is unreachable.
