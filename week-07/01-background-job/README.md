# Assignment A7: Your First Background Job

> **FlyRank Backend Internship · Week 4 / Week 7 Assignment A7**  
> Build a small API whose slow work happens in a background job — the endpoint answers instantly, a status endpoint reports progress, and one cron job runs on the clock alone.

---

## Goals & Big Idea

- **Pattern**: Accept fast (`202 Accepted`), work in the background (durable jobs), report status (`GET /reports/:id`).
- **Resilience**: Automatic retries with exponential backoff on temporary failures; strict input validation (`400 Bad Request`) for invalid payloads without retrying.
- **Scheduling**: Cron-triggered background heartbeat function (`* * * * *`).

---

## Tech Stack & Tools

- **Language**: Python 3.10+ (FastAPI) or Node.js (Express)
- **Background Jobs**: Inngest (`inngest` SDK + Inngest Dev Server at `http://localhost:8288`)
- **Testing**: `curl`, browser, Inngest Dashboard

---

## Stages & Milestones

### Stage 0: Hello Server (~30 min)
- Create server with `GET /health` returning `{"status": "ok"}`.
- **Checkpoint**: `curl -i http://localhost:8000/health` returns `200 OK`.
- *Commit*: `Stage 0: hello server`

### Stage 1: Connect Inngest (~1 h)
- Install Inngest SDK.
- Create Inngest client (id: `report-api`).
- Define function `say-hello` triggered by `test/hello`, sleeps 5 seconds (`step.sleep`), returns `"Hello from the background!"`.
- Serve Inngest handler at `/api/inngest`.
- **Checkpoint**: Inngest Dev Server dashboard shows `say-hello` run ending with status `Completed`.
- *Commit*: `Stage 1: Inngest connected, first function runs`

### Stage 2: Fast Door: Accept Now, Work Later (~1.5 h)
- In-memory dictionary/map for reports.
- `POST /reports` with `{"topic": "cats"}`:
  - Generates ID, sets status `"pending"`.
  - Sends `report/requested` event with ID and topic.
  - Returns `202 Accepted` immediately with `{"id": "...", "status": "pending"}`.
- Inngest function `make-report`:
  - `step.sleep("do-the-slow-work", "8s")`
  - `step.run("build-report", ...)` saves result and status `"done"`.
- Status endpoint `GET /reports/:id` returning object (`pending` → `done`).
- **Checkpoint**: `POST /reports` returns in <1s; `GET /reports/:id` transitions from `pending` to `done`.
- *Commit*: `Stage 2: 202 + background job + status endpoint`

### Stage 3: Jobs Fail. Watch the Retry (~45 min)
- In `make-report`: if topic is `"fail"`, raise an error (`"The report oven is broken!"`).
- Configure `retries=2` in `create_function`.
- Validation on `POST /reports`: if topic is missing, return `400 Bad Request` and do not send an event.
- **Checkpoint**: `POST /reports` with `{"topic": "fail"}` triggers 3 attempts with backoff ending in `Failed`. Missing topic returns `400`.
- *Commit*: `Stage 3: retries seen, bad input rejected`

### Stage 4: The Clock Knocks: Your First Cron Job (~45 min)
- Function `heartbeat` with cron trigger `* * * * *`.
- Summarizes count of reports: `pending`, `done`, `failed`.
- **Checkpoint**: Dashboard shows heartbeat runs every minute logging the summary.
- *Commit*: `Stage 4: cron heartbeat`

### Stage 5: Publish & Documentation (~45 min)
- Document API commands, dev server commands, endpoint table, and pasted proofs.
- *Commit*: `Stage 5: publish and docs`

### Stage 6 (Bonus): AI Rematch (~1 h)
- Prompt an AI model to recreate the spec, compare side-by-side with `git diff --no-index`.
- *Commit*: `Stage 6: AI vs me`

---

## Running Locally

```bash
# Terminal 1: Run the API server
uvicorn app.main:app --port 8000 --reload

# Terminal 2: Run Inngest Dev Server
npx inngest-cli@latest dev -u http://localhost:8000/api/inngest
```
- API Documentation: `http://localhost:8000/docs`
- Inngest Dashboard: `http://localhost:8288`
