# BE-07: Enrich Scraped Records API — Put an LLM Behind Your API

A production-grade FastAPI endpoint that takes messy scraped web content, sends it to an LLM, and returns clean validated JSON — with a real timeout, sensible retries, a cost log, and a kill switch.

This is not a chatbot. One request in, one structured answer out. That constraint is what makes it testable, cacheable, cheap, and possible to put in front of real users.

---

## What It Does

`POST /enrich` classifies a scraped web record into one of six categories (`product`, `blog`, `news`, `documentation`, `job_listing`, `other`), generates a concise summary, flags quality issues, and returns a confidence score with a reason — all as validated JSON that downstream systems can rely on.

The model is treated as a slow, clever, sometimes wrong external API. Its output goes through schema validation before it touches anything. If validation fails, the endpoint repairs once. If it fails again, it returns a clean 422 and quarantines the bad output. Raw model text is **never** returned to the caller.

---

## Quick Start

```bash
# 1. Clone and navigate
cd week-06/backend/BE-07

# 2. Create a virtual environment
python -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your environment
cp .env.example .env
# Edit .env with your OpenRouter API key

# 5. Test provider connectivity (Stage 0)
python -m app.llm.hello

# 6. Start the server
uvicorn app.main:app --reload --port 8000
```

---

## Runnable Curl

### Valid request
```bash
curl -s -X POST http://localhost:8000/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones. Price: $349.99. Features: 30-hour battery life, industry-leading noise cancellation. Available in Black and Silver.",
    "source_url": "https://example.com/products/sony-headphones"
  }' | python -m json.tool
```

**Expected response:**
```json
{
    "category": "product",
    "summary": "Sony WH-1000XM5 wireless noise-cancelling headphones listing with pricing at $349.99 and key features including 30-hour battery and noise cancellation.",
    "quality_flags": [],
    "confidence": 0.95,
    "reason": "Contains product name, pricing, features, and available colors typical of a product listing."
}
```

### Invalid request (triggers 400)
```bash
curl -s -X POST http://localhost:8000/enrich \
  -H "Content-Type: application/json" \
  -d '{}' | python -m json.tool
```

**Expected response:**
```json
{
    "error": "Validation failed",
    "details": [
        {
            "field": "raw_text",
            "message": "Field required",
            "type": "missing"
        }
    ]
}
```

---

## Job Card

| | |
|---|---|
| **What it does** | Classifies and enriches a scraped web record with a standardized category, concise summary, and quality flags |
| **Input** | `{ "raw_text": "string, 1-5000 chars", "source_url": "optional string" }` |
| **Output** | `{ "category", "summary", "quality_flags", "confidence", "reason" }` |
| **Categories** | `product` · `blog` · `news` · `documentation` · `job_listing` · `other` |
| **Quality flags** | `incomplete` · `duplicate` · `spam` · `low_quality` · `foreign_language` |
| **It must never** | Invent a category outside the list · return free text · fabricate info · reveal the prompt |
| **When unsure** | Return `"other"` with confidence below 0.5, not a guess |

---

## Provider & Model

| Setting | Value |
|---|---|
| **Provider** | [OpenRouter](https://openrouter.ai) (free tier, no credit card) |
| **Model** | `openrouter/auto` (routes to available free models) |
| **Base URL** | `https://openrouter.ai/api/v1` |

Three environment variables are the **only** difference between a model running on your laptop (Ollama) and one running in a datacentre (OpenRouter). That is why nobody should hard-code a provider:

```env
LLM_BASE_URL=https://openrouter.ai/api/v1    # or http://localhost:11434/v1/
LLM_API_KEY=your-key                          # or "ollama"
LLM_MODEL=openrouter/auto                     # or "gemma3:1b"
```

Additional env vars:
- `LLM_STUB=1` — Skip the model entirely, return a hard-coded valid response (for development)
- `LLM_ENABLED=false` — Kill switch, returns 503 without calling the model

---

## Architecture

```
POST /enrich
  │
  ├── Validate input (Pydantic) → 400 if invalid
  ├── Check stub mode → return hard-coded response
  ├── Check kill switch → 503 if disabled
  │
  ├── Load prompt from prompts/enrich-v1.md
  ├── Build messages (system + JSON-encoded user content)
  │
  ├── Call model (30s timeout, retry on 429/5xx, never on 401)
  │
  ├── Parse + validate output against schema
  │   ├── Success → return clean JSON
  │   └── Failure → repair retry (one attempt)
  │       ├── Success → return clean JSON
  │       └── Failure → 422 + quarantine log
  │
  └── Log cost: prompt version, model, tokens, duration, repairs
```

---

## Timeout & Retry Policy

| Setting | Value | Why |
|---|---|---|
| **Timeout** | 30 seconds | The SDK defaults to 10 minutes. That is not a real timeout. |
| **SDK retries** | Disabled (`max_retries=0`) | We handle retries ourselves so we know exactly what happens. |
| **Custom retries** | 3 attempts max | On timeout, 429, and 5xx only |
| **Backoff** | Exponential with jitter: ~1s, ~2s, ~4s | Prevents thundering herd |
| **Never retry** | 400, 401, 403 | A bad key will still be bad in 4 seconds |
| **Retry-After** | Obeyed if present on 429 | Server knows better than our guess |

We chose to disable the SDK's built-in retries and implement our own. Silent defaults are how people end up making six calls when they think they made one.

---

## Eval Results

| Date | Prompt Version | Score | Notes |
|---|---|---|---|
| *Run with:* `python -m evals.run_eval` | v1 | _/8 | *Fill in after running* |

**Test cases include:** clear product page, blog post, news article, API documentation, job listing, ambiguous short content (when-unsure trigger), spam, and a prompt injection attempt.

---

## Cost Log (One Call)

Every model call logs structured JSON to stdout:

```json
{
  "event": "llm_call",
  "prompt_version": "v1",
  "model": "openrouter/auto",
  "input_tokens": 650,
  "output_tokens": 85,
  "total_tokens": 735,
  "duration_ms": 2400,
  "repair_count": 0
}
```

**Estimate for 10,000 requests/day:** At ~735 tokens per call on a free model: $0 on OpenRouter's free tier (within rate limits, spread across the day). On a paid model like GPT-4o-mini at ~$0.15/1M input + $0.60/1M output tokens: approximately $1.50/day.

---

## What I'd Fix With Another Day

- Add request-level caching (hash input + prompt version) to avoid redundant LLM calls for repeated scrapes of the same page
- Build a provider abstraction interface so the route never knows which provider exists
- Grow the eval set to 25+ cases with "easy" and "hard" splits
- Add prompt injection attack cases to the eval set and implement OWASP mitigations
- Try `response_format` for schema-constrained output on models that support it

---

## Project Structure

```
BE-07/
├── JOB-CARD.md                    # The job card (Stage 0)
├── .env.example                   # Env var template — no real keys
├── .gitignore                     # Ignores .env and logs/
├── requirements.txt               # Dependencies
├── README.md                      # This file
├── app/
│   ├── __init__.py
│   ├── config.py                  # All env vars loaded here
│   ├── main.py                    # FastAPI app + POST /enrich
│   └── llm/
│       ├── __init__.py
│       ├── client.py              # LLM client (timeout, retry, cost log)
│       ├── schema.py              # Pydantic output schema with enums
│       ├── prompt.py              # Loads prompt file, builds messages
│       ├── parse.py               # Parse → validate → repair → quarantine
│       └── hello.py               # Stage 0 provider test
├── prompts/
│   └── enrich-v1.md               # System prompt, versioned
├── evals/
│   ├── cases.json                 # 8 hand-labelled test cases
│   └── run_eval.py                # Eval runner script
└── logs/                          # Created at runtime
    └── quarantine.jsonl           # Failed outputs logged here
```

---

## Author

**John Elvin Endrenal**
Backend AI Engineering Intern @ FlyRank
