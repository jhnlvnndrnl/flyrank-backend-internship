# BE-02: To-Do List CRUD API

A lightweight, robust backend REST API for managing a to-do list, built with **Python 3.10+** and **FastAPI**.

---

## 🚀 Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Server
```bash
uvicorn app.main:app --reload
```
The server will start on `http://localhost:8000`.

---

## 📑 API Endpoints Summary

| CRUD Operation | HTTP Method | Path | Description | Success Code | Error Codes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Root** | `GET` | `/` | API metadata and endpoint list | `200 OK` | - |
| **Health** | `GET` | `/health` | Server health check | `200 OK` | - |
| **Read** | `GET` | `/tasks` | List all tasks (supports `?done=true` and `?search=keyword`) | `200 OK` | - |
| **Read** | `GET` | `/tasks/{id}` | Get a single task by ID | `200 OK` | `404 Not Found` |
| **Create** | `POST` | `/tasks` | Create a new task | `201 Created` | `400 Bad Request` |
| **Update** | `PUT` | `/tasks/{id}` | Update title and/or completion status of a task | `200 OK` | `400 Bad Request`, `404 Not Found` |
| **Delete** | `DELETE` | `/tasks/{id}` | Delete a task by ID | `204 No Content` | `404 Not Found` |
| **Stats** | `GET` | `/stats` | Aggregate task statistics (total, done, open) | `200 OK` | - |
| **Reset** | `POST` | `/reset` | Reset task list to initial seed data | `200 OK` | - |

---

## 🔍 Swagger UI Interactive Documentation

FastAPI provides built-in interactive OpenAPI documentation.

Once the server is running, open your browser and navigate to:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

You can test all endpoints interactively using the **"Try it out"** button.

---

## 💻 Sample `curl -i` Verification Outputs

### 1. Root Endpoint (`GET /`)
```bash
$ curl -i http://localhost:8000/
HTTP/1.1 200 OK
date: Fri, 31 Jul 2026 13:52:00 GMT
server: uvicorn
content-length: 56
content-type: application/json

{"name":"Task API","version":"1.0","endpoints":["/tasks"]}
```

### 2. Create Task (`POST /tasks`)
```bash
$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
HTTP/1.1 201 Created
date: Fri, 31 Jul 2026 13:52:00 GMT
server: uvicorn
content-length: 44
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

### 3. Validation Error (`POST /tasks` with empty payload)
```bash
$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{}'
HTTP/1.1 400 Bad Request
date: Fri, 31 Jul 2026 13:52:00 GMT
server: uvicorn
content-length: 33
content-type: application/json

{"error":"Title is required"}
```

### 4. Update Task (`PUT /tasks/4`)
```bash
$ curl -i -X PUT http://localhost:8000/tasks/4 -H "Content-Type: application/json" -d '{"done":true}'
HTTP/1.1 200 OK
date: Fri, 31 Jul 2026 13:52:00 GMT
server: uvicorn
content-length: 43
content-type: application/json

{"id":4,"title":"Buy milk","done":true}
```

### 5. Delete Task (`DELETE /tasks/4`)
```bash
$ curl -i -X DELETE http://localhost:8000/tasks/4
HTTP/1.1 204 No Content
date: Fri, 31 Jul 2026 13:52:00 GMT
server: uvicorn
```

### 6. Unknown Task Error (`GET /tasks/99`)
```bash
$ curl -i http://localhost:8000/tasks/99
HTTP/1.1 404 Not Found
date: Fri, 31 Jul 2026 13:52:00 GMT
server: uvicorn
content-length: 29
content-type: application/json

{"error":"Task 99 not found"}
```

---

## 🧠 Mortality Experiment (In-Memory Data)

When tasks are created, updated, or deleted, the changes persist only in the Python server process memory. If the server is restarted, all newly created tasks disappear and the database resets to the initial 3 seed tasks. 

**Observation:** In-memory storage is fast and zero-overhead for development, but volatile. Applications require persistent databases (e.g., PostgreSQL, SQLite) to maintain state across restarts and server deployments.

---

## 🤖 AI vs Me Section

### Prompt Used:
> "Build a CRUD API using Python and FastAPI for managing a to-do list in memory. The API must have GET /, GET /health, GET /tasks, GET /tasks/{id}, POST /tasks, PUT /tasks/{id}, and DELETE /tasks/{id}. Ensure POST and PUT return 400 with a JSON error if title is empty or missing, 404 for missing IDs, 201 for create, and 204 for delete. Include interactive Swagger docs."

### Comparison Summary:
1. **Validation & Exception Handling:** The hand-crafted code explicitly overrides FastAPI's default `RequestValidationError` to guarantee custom `400 Bad Request` JSON responses (`{"error": "..."}`) rather than defaulting to `422 Unprocessable Entity`.
2. **Status Codes:** Both implementations correctly handled HTTP `201 Created` and HTTP `204 No Content`.
3. **Extras:** The hand-crafted version includes query parameter filtering (`?done=true`, `?search=...`), aggregate `/stats`, and a `/reset` endpoint.