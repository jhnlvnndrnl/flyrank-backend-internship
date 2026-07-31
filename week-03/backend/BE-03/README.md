# BE-03: Connecting your CRUD to SQLite Database

A production-grade RESTful CRUD API built with **Python 3.10+** and **FastAPI**, backed by a real **SQLite** database (`tasks.db`) for data persistence across server restarts.

---

## Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
uvicorn app.main:app --reload
```
The server starts on `http://localhost:8000`. On first run, SQLite automatically creates `tasks.db`, builds the `tasks` table, and seeds initial data.

---

## Why SQLite?

- **Zero Config & Serverless**: SQLite requires no external database server process; it operates entirely within a single file (`tasks.db`).
- **Data Persistence**: Replaces in-memory lists so tasks survive application restarts.
- **Python Standard Library**: Powered by Python's built-in `sqlite3` module.

---

## Database Architecture

### File Location
- Path: `week-03/backend/BE-03/tasks.db`
- *Note:* `tasks.db` is git-ignored so each clone initializes fresh database schemas automatically.

### Table Schema (`tasks`)
```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 0
);
```

---

## Parameterized SQL Queries Used

All database interactions use **parameterized query placeholders (`?`)** to guarantee protection against SQL injection vulnerabilities:

- **Read All / Filter**:
  ```sql
  SELECT * FROM tasks WHERE done = ? AND title LIKE ? ORDER BY id ASC;
  ```
- **Read One**:
  ```sql
  SELECT * FROM tasks WHERE id = ?;
  ```
- **Insert**:
  ```sql
  INSERT INTO tasks (title, done) VALUES (?, ?);
  ```
- **Update**:
  ```sql
  UPDATE tasks SET title = ?, done = ? WHERE id = ?;
  ```
- **Delete**:
  ```sql
  DELETE FROM tasks WHERE id = ?;
  ```
- **Stats**:
  ```sql
  SELECT COUNT(*) FROM tasks;
  SELECT COUNT(*) FROM tasks WHERE done = 1;
  ```

---

## API Endpoints Summary

| CRUD Operation | HTTP Method | Path | Description | Success Code | Error Codes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Root** | `GET` | `/` | API description & metadata | `200 OK` | - |
| **Health** | `GET` | `/health` | Server health check | `200 OK` | - |
| **Read All** | `GET` | `/tasks` | List tasks (supports `?done=true`, `?search=keyword`, `?sort=title`) | `200 OK` | - |
| **Read One** | `GET` | `/tasks/{id}` | Retrieve a task by ID | `200 OK` | `404 Not Found` |
| **Create** | `POST` | `/tasks` | Insert a new task | `201 Created` | `400 Bad Request` |
| **Update** | `PUT` | `/tasks/{id}` | Update title/completion of a task | `200 OK` | `400 Bad Request`, `404 Not Found` |
| **Delete** | `DELETE` | `/tasks/{id}` | Remove a task by ID | `204 No Content` | `404 Not Found` |
| **Stats** | `GET` | `/stats` | Aggregated statistics via SQL `COUNT()` | `200 OK` | - |
| **Reset** | `POST` | `/reset` | Re-initialize database seed tasks | `200 OK` | - |

---

## Interactive Swagger UI Documentation

Access live OpenAPI documentation at:
**[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## Hand-executed SQL Exploration (DB Browser for SQLite)

Ran and verified the following SQL queries directly against `tasks.db`:

```sql
-- 1. List all tasks
SELECT * FROM tasks;

-- 2. List completed tasks
SELECT * FROM tasks WHERE done = 1;

-- 3. Aggregate total count
SELECT COUNT(*) FROM tasks;

-- 4. Mark all completed
UPDATE tasks SET done = 1;

-- 5. Remove completed tasks
DELETE FROM tasks WHERE done = 1;
```

---

## AI vs Me Section

### Prompt Used:
> "Migrate an in-memory FastAPI CRUD API to a SQLite database using Python's built-in sqlite3. Use parameterized queries with ? placeholders. Ensure table is created if missing and seeded with 3 tasks only when empty. Retain exact HTTP status codes (200, 201, 204, 400, 404) and JSON error formats."

### Concrete Differences:
1. **Idempotent Seeding**: AI initially omitted `COUNT(*)` checks, causing seed tasks to duplicate on every application restart. The hand-crafted implementation correctly verifies `COUNT(*) == 0` prior to inserting seed rows.
2. **Custom Error Handling**: Hand-crafted version preserves custom `400 Bad Request` JSON overrides for empty titles (`{"error": "Title cannot be empty"}`), while AI defaulted to standard FastAPI `422 Unprocessable Entity`.
3. **Connection Management**: The hand-crafted code uses `sqlite3.Row` for dict-like column access and clean connection handling.
