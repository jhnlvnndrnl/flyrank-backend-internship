# 🚀 FlyRank Backend Engineering Internship

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0-6BA539?style=for-the-badge&logo=openapi-initiative&logoColor=white)](https://swagger.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

> A centralized repository documenting backend engineering projects, RESTful API developments, and AI fluency exercises completed during the **FlyRank Backend Engineering Internship**.

---

## 📌 Overview

This repository serves as a centralized hub for all weekly engineering deliverables, API implementations, and technical case studies. Rather than fragmenting assignments across isolated repositories, this mono-repo preserves complete git history, architectural progression, and clean modular organization.

---

## 🗺 Repository Architecture

```text
assignment/
├── README.md                      # Primary Internship Overview
├── .gitignore                     # Git ignore rules
│
├── week-01/                        # Week 1: Foundational Workflow & AI Toolkit
│   ├── README.md                  # Week 1 summary
│   └── fluency/
│       ├── FL-01/                 # AI Workflow Audit & Tool Setup
│       ├── FL-02/                 # Portfolio Architecture & Sitemap
│       └── FL-03/                 # Portfolio Positioning & Proof Statements
│
├── week-02/                        # Week 2: RESTful API Design & Prompt Engineering
│   ├── README.md                  # Week 2 summary
│   ├── backend/
│   │   └── BE-02/                 # FastAPI To-Do List CRUD API
│   │       ├── README.md          # BE-02 API Documentation & OpenAPI Specs
│   │       ├── requirements.txt   # Dependencies
│   │       └── app/
│   │           └── main.py        # FastAPI CRUD implementation & custom validation
│   └── fluency/
│       ├── FL-04/                 # Case Framing & Systems Analysis
│       ├── FL-05/                 # Prompt Laddering & Iteration Benchmark
│       └── FL-06/                 # Prompting Fundamentals on Real Tasks
│
├── week-03/                        # Week 3: Persistence & Database Integration (Upcoming)
│   ├── README.md
│   ├── backend/
│   └── fluency/
│
└── docs/                           # Central Knowledge & Reference Docs
    ├── resources.md               # Curated learning resources & references
    └── notes.md                   # Engineering notes & architectural decisions
```

---

## 🗓 Weekly Deliverables Matrix

| Week | Track | Module | Description | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Week 1** | **Fluency** | [`FL-01`](week-01/fluency/FL-01/workflow-audit.md) | AI Workflow Audit & Tool Setup | `Completed` |
| **Week 1** | **Fluency** | [`FL-02`](week-01/fluency/FL-02/draw-the-path.md) | Draw the Path — Portfolio Sitemap & Pressure Testing | `Completed` |
| **Week 1** | **Fluency** | [`FL-03`](week-01/fluency/FL-03/what-are-you-proving.md) | Portfolio Positioning & Proof Statement | `Completed` |
| **Week 2** | **Backend** | [`BE-02`](week-02/backend/BE-02/README.md) | **FastAPI To-Do List CRUD API** with Swagger UI & custom error handling | `Completed` |
| **Week 2** | **Fluency** | [`FL-04`](week-02/fluency/FL-04/frame-it_as_cases.md) | Frame It As Cases — Structured Systems Analysis | `Completed` |
| **Week 2** | **Fluency** | [`FL-05`](week-02/fluency/FL-05/prompt_ladder.md) | Prompt Laddering & Output Comparison Benchmarks | `Completed` |
| **Week 2** | **Fluency** | [`FL-06`](week-02/fluency/FL-06/Prompting_Fundamentals_on_Real_Tasks_v2.md) | Prompting Fundamentals on Real Tasks | `Completed` |
| **Week 3** | **Backend** | `BE-03` | Database Integration & Persistent Storage | `In Progress` |

---

## ⚡ Featured Project: FastAPI CRUD API (BE-02)

The **BE-02** module is a lightweight, production-grade RESTful CRUD API built with **FastAPI**.

### Key Features
- 🔄 **Full CRUD Operations**: Endpoints for creating (`POST`), reading (`GET`), updating (`PUT`), and deleting (`DELETE`) tasks.
- 🎯 **Custom Input Validation**: Overridden exception handlers returning explicit HTTP `400 Bad Request` JSON responses (`{"error": "..."}`) for empty or missing payloads.
- 📖 **Interactive OpenAPI Documentation**: Built-in Swagger UI at `/docs`.
- 🔍 **Filtering & Search**: Support for completion status query filters (`?done=true`) and search (`?search=keyword`).
- 📊 **Stats & Reset Utilities**: Aggregated metrics (`GET /stats`) and database reset (`POST /reset`).

### Quick Run Instructions
```bash
# 1. Navigate to the project directory
cd week-02/backend/BE-02

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the development server
uvicorn app.main:app --reload
```
View the live interactive API documentation at 👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**.

---

## 🛠 Technology Stack

- **Backend Framework**: Python 3.10+, FastAPI, Uvicorn (ASGI Server)
- **API Standards**: RESTful API design, OpenAPI 3.0, Swagger UI
- **Data Validation**: Pydantic, Custom FastAPI Exception Handlers
- **Tooling & VCS**: Git, GitHub, Markdown, cURL

---

## 👨‍💻 Author

**John Elvin Endrenal**  
Backend AI Engineering Intern @ FlyRank  
GitHub: [@jhnlvnndrnl](https://github.com/jhnlvnndrnl)