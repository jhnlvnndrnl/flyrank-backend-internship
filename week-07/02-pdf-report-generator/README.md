# Assignment A8: PDF Report Generator

> **FlyRank Backend Internship · Week 4 / Week 7 Assignment A8**  
> Query your data with SQL, render it into a real PDF report, and let your API generate and hand out the file by link — no background jobs required for the core pipeline.

---

## Goals & The 4-Step Pipeline

```text
[ Query (SQL Aggregations) ] ──> [ Render (HTML + Playwright PDF) ] ──> [ Store (Disk Artifact) ] ──> [ Serve (File Link) ]
```

- **Rule**: *Store and link, don't pass bytes around.* A PDF is an artifact saved to disk, while JSON endpoints pass its URI.
- **Idempotency**: Multiple requests on the same day return the existing generated report rather than duplicating file generation.

---

## Tech Stack & Tools

- **Language & Framework**: Python 3.10+ (FastAPI) or Node.js (Express)
- **Database**: SQLite (built-in `sqlite3` in Python / `node:sqlite` in Node.js)
- **PDF Engine**: Playwright Headless Chromium (`page.pdf({ format: "A4", printBackground: true })`)
- **Testing**: `curl`, browser, PDF viewer

---

## Stages & Milestones

### Stage 0: Setup (~30 min)
- Create base server with `GET /health` → `{"status": "ok"}`.
- Install Playwright & Chromium: `pip install playwright && playwright install chromium` or `npm install playwright && npx playwright install chromium`.
- *Commit*: `Stage 0: setup ready`

### Stage 1: Data Worth Reporting On (~45 min)
- Create SQLite DB `report.db` with `orders` table (or reuse `books` table from A9).
- Write `seed` script that populates ~200 rows and cleans up before insertion (idempotent seed).
- *Commit*: `Stage 1: seeded report.db`

### Stage 2: SQL Aggregation Queries (~1 h)
- Implement `getReportData()` with 4 aggregate queries:
  1. Total number of orders (`COUNT(*)`)
  2. Total revenue (`SUM(amount)`)
  3. Top 5 products by revenue (`GROUP BY product ORDER BY revenue DESC LIMIT 5`)
  4. Orders per day for the last 7 days (`GROUP BY date(created_at)`)
- *Commit*: `Stage 2: aggregation queries`

### Stage 3: Render HTML to PDF (~1.5 h)
- Build clean HTML report template from the aggregated metrics.
- Render with Playwright headless Chromium.
- Handle CSS print page-breaks: `tr { break-inside: avoid; }`, `thead` repetition across pages.
- *Commit*: `Stage 3: HTML to PDF with clean page breaks`

### Stage 4: Serve from API (~45 min)
- Create `reports` table in `report.db` (`id`, `path`, `created_at`).
- `POST /reports`: executes query → renders PDF to `reports/<id>.pdf` → records in DB → returns `201 Created` with `{"id": "...", "file": "/reports/<id>/file"}`.
- `GET /reports/:id`: returns metadata JSON.
- `GET /reports/:id/file`: serves actual PDF file (`FileResponse` / `res.sendFile`).
- *Commit*: `Stage 4: generate and serve by link`

### Stage 5: Ask Twice, Get One (Idempotency) (~30 min)
- Check if report was already generated today. If yes, return existing record with `200 OK`.
- Support `{ "force": true }` to bypass cache and regenerate.
- *Commit*: `Stage 5: duplicate requests make one report`

### Stage 6: Publish & Docs (~45 min)
- Documentation, run commands, SQL queries, download proofs, and PDF screenshots.
- Ensure `reports/` and `report.db` are in `.gitignore`.
- *Commit*: `Stage 6: publish and docs`

### Stage 7 (Bonus): AI Rematch (~1 h)
- Prompt AI to generate the pipeline, benchmark against manual implementation.
- *Commit*: `Stage 7: AI vs me`
