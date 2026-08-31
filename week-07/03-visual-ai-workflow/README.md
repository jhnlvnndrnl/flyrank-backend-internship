# Visual AI Workflow System

> **FlyRank Internship · Week 7 Assignment: Visual AI Workflow System**  
> Build a visual AI workflow system where each node represents an AI decision step that returns either `YES` or `NO`. The workflow execution runs through Inngest while the frontend visualizes the flow using React Flow.

---

## System Architecture

```text
┌────────────────────────────────────────────────────────┐
│                   React Flow Canvas                    │
│  [ Start Node ] ──> [ AI Decision Node ] ──YES──> ...  │
│                                          ──NO───> ...  │
└───────────────────────────┬────────────────────────────┘
                            │ (Trigger Run / Sync State)
                            ▼
┌────────────────────────────────────────────────────────┐
│              Inngest Workflow Orchestrator             │
│  - Step 1: Evaluate AI Decision Node Prompt via LLM    │
│  - Step 2: Traverse graph along YES/NO active edge     │
│  - Step 3: Stream/record node execution status & logs  │
└───────────────────────────┬────────────────────────────┘
                            │ (Evaluation)
                            ▼
┌────────────────────────────────────────────────────────┐
│                    LLM (OpenAI API)                    │
│      Strict Boolean Classification Output: YES / NO     │
└────────────────────────────────────────────────────────┘
```

---

## Technology Stack

- **Frontend**: Next.js / React, React Flow (`@xyflow/react`), TailwindCSS / Shadcn UI
- **Workflow Engine**: Inngest (`inngest` client + dev server)
- **AI / LLM**: OpenAI SDK / Gemini API
- **State Management**: Local React state, LocalStorage / JSON persistence

---

## Implementation Phases

### Phase 1: Setup (Estimated: ~1 h)
- **Goal**: Initialize the project and prepare the development environment.
- **Requirements**:
  - Create a React or Next.js application.
  - Install & configure dependencies: `@xyflow/react`, `inngest`, `openai`, `lucide-react`, Shadcn UI.
  - Configure environment variables (`OPENAI_API_KEY` / `GEMINI_API_KEY`, `INNGEST_EVENT_KEY`, `INNGEST_SIGNING_KEY`).
  - Set up a clean project structure.
- **Deliverables**:
  - Running frontend application.
  - Working Inngest dev server.
  - Initialized repository with README.

### Phase 2: Foundations — Visual Flow Editor (Estimated: ~2 h)
- **Goal**: Build the visual flow editor and graph structure.
- **Requirements**:
  - Render a React Flow canvas with custom nodes and controls.
  - Add, delete, and connect nodes.
  - Editable node prompts (input system & user instructions).
  - Define custom edge types:
    - `YES` path (e.g. green styling / label)
    - `NO` path (e.g. red styling / label)
  - Store graph state locally.
- **Deliverables**:
  - Interactive flow editor.
  - Custom editable decision prompt nodes.
  - Functional node connections with labeled condition edges.

### Phase 3: Build (Core) — Inngest & AI Execution (Estimated: ~2 h)
- **Goal**: Execute the workflow using Inngest and AI responses.
- **Requirements**:
  - Each node maps to a discrete Inngest step.
  - Send the node prompt + input context to the LLM.
  - Strict classification: model must return only **`YES`** or **`NO`**.
  - Continue traversal dynamically based on the returned edge:
    - *Example*: `"Is this a support request?"`
      - `YES` ──> Support Handling Node
      - `NO` ──> Sales Inquiry Node
  - Track execution order and step timing.
- **Deliverables**:
  - End-to-end workflow execution.
  - Dynamic node traversal powered by AI boolean branching.

### Phase 4: Build (Polish) — UI/UX & DX (Estimated: ~2 h)
- **Goal**: Improve usability, observability, and developer experience.
- **Requirements (Select at least 3)**:
  - [x] **Visual Execution State**: Real-time highlighting of active/completed/failed nodes on the canvas.
  - [x] **Execution Logs Panel**: Step-by-step audit logs showing prompts, LLM tokens, and decision rationale.
  - [x] **Save / Load Workflows & JSON Import / Export**: Template management for common decision trees.
  - [x] **Animated Active Edges**: Visual pulses across traversed branches.
  - [x] **Error Handling & Retry Mechanism**: Graceful recovery on LLM timeout or invalid response.
  - [x] **Execution History**: Persistent list of past workflow runs and their final states.
- **Deliverables**:
  - Polished UI/UX with responsive design.
  - Robust execution telemetry and error handling.
