# Week 07: Distributed Workflows, Background Processing & Visual AI Systems

This directory contains the Week 7 internship deliverables focusing on asynchronous job orchestration, automated artifact generation, and visual AI graph workflows.

---

## Deliverables Summary

| # | Assignment | Module | Tech Stack | Description |
| :--- | :--- | :--- | :--- | :--- |
| **01** | **Assignment A7** | [`01-background-job`](01-background-job/README.md) | FastAPI / Express, Inngest, Cron | **Your First Background Job**: Event-driven asynchronous execution, 202 Accepted + polling pattern, exponential backoff retries, and cron heartbeat monitor. |
| **02** | **Assignment A8** | [`02-pdf-report-generator`](02-pdf-report-generator/README.md) | SQLite, Playwright, HTML/CSS | **PDF Report Generator**: Relational data aggregation, HTML-to-PDF headless browser rendering, artifact store-and-link pattern, and idempotent generation. |
| **03** | **Visual AI Workflow** | [`03-visual-ai-workflow`](03-visual-ai-workflow/README.md) | React / Next.js, React Flow, Inngest, OpenAI SDK, Shadcn | **Visual AI Workflow System**: Interactive node-based graph editor where each AI decision step branches dynamically on YES / NO conditions via Inngest step orchestration. |

---

## Directory Structure

```text
week-07/
├── README.md                           # Week 7 Overview & Index
│
├── 01-background-job/                  # Assignment A7: Asynchronous background jobs with Inngest
│   └── README.md                       # A7 Specification, stages & checkpoints
│
├── 02-pdf-report-generator/            # Assignment A8: SQL Aggregation & Playwright PDF pipeline
│   └── README.md                       # A8 Specification, stages & checkpoints
│
└── 03-visual-ai-workflow/              # Visual AI Decision Workflow System
    └── README.md                       # Phases 1-4 Specs, React Flow & Inngest architecture
```
