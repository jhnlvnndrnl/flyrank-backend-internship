# Week 05: Web Scraping & Data Pipelines

This directory contains the Week 5 internship deliverable focusing on a polite, deterministic
scraping pipeline — fetch, extract, normalize, validate, store, and report — built against a
public practice sandbox (Books to Scrape).

---

## Deliverables Summary

- **Backend Track (`A9`)**: [`week-05`](week-05/README.md) — **The Polite Scraper**
  - Crawls the first 3 catalogue pages and discovers all 60 unique book detail URLs.
  - Polite fetcher: identifying `User-Agent`, request timeout, status-code check, on-disk HTML cache.
  - HTML extraction with BeautifulSoup into 8 raw fields per book (title, URL, price, availability, rating, description, source page, fetched-at timestamp).
  - Normalization (`price_text` → `price_gbp`) and schema validation with Pydantic.
  - Idempotent storage — reruns update `books.json` in place, never duplicate records.
  - Graceful failure handling — one broken URL is logged to `errors.json`, the other 59+ records survive.
  - Honest run report (`run-report.json`) with duration, pages fetched, cache hits, valid/invalid counts, and failed pages.
  - `ai-version/` — an isolated AI-generated rematch of the same spec, diffed against the hand-built version.

---

## Target Classification

- **Target**: [Books to Scrape](https://books.toscrape.com) — a public sandbox built specifically for scraping practice.
- **Scope**: the first 3 catalogue pages only (`page-1.html` → `page-3.html`), followed via the site's own "next" links.
- **`robots.txt` check**: `https://books.toscrape.com/robots.txt` → *[paste what the request actually returned here, e.g. "no robots file found" or its contents]*
- **Data collected**: title, product URL, price, availability, star rating, description, source page, fetch timestamp — nothing beyond what's needed to build the validated record.
- This site exists explicitly for scraping practice, so automated access here is appropriate. This code will not be reused on another site without checking that site's own rules and terms first.

---

## Politeness Rules

Every real (non-cached) request:
- Sends an identifying `User-Agent` (e.g. `FlyRankInternshipA9/1.0 (+link-to-repo)`).
- Has a request timeout — it never waits forever.
- Checks the HTTP status code before parsing; only `200` is treated as a successful fetch.
- Waits at least 500ms between live requests. Cached pages are read from disk and incur no delay.
- Development and repeat runs read from `cache/` instead of re-hitting the site.

---

## Pipeline

| Stage | What it does |
|---|---|
| Crawl | Follows the catalogue's own "next" links across 3 pages, collects and deduplicates all book URLs. |
| Fetch | Downloads each page with caching, a timeout, and a status check. |
| Extract | Parses raw fields from each book detail page with BeautifulSoup. |
| Normalize | Converts `price_text` (`"£51.77"`) into a numeric `price_gbp`. |
| Validate | Checks every record against a Pydantic schema; failures are set aside with a reason. |
| Store | Writes validated records to `output/books.json`, keyed by canonical `product_url` for idempotency. |
| Report | Writes `output/run-report.json` with counts and timing for the run. |

## Record Schema

```json
{
  "title": "A Light in the Attic",
  "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "price_text": "£51.77",
  "price_gbp": 51.77,
  "availability_text": "In stock (22 available)",
  "rating_text": "Three",
  "description": "...",
  "source_page": "https://books.toscrape.com/catalogue/page-1.html",
  "fetched_at": "2026-08-06T10:00:00Z"
}
```

Records that fail validation are written to `errors.json` with the original raw data and a reason,
and never reach `books.json`.

---

## How to Run

```bash
# from week-05/ai-version (or your hand-built equivalent)
pip3 install requests pydantic beautifulsoup4
python3 src/main.py                  # normal run
python3 src/main.py --inject-broken  # adds one fake URL to test failure handling
python3 src/main.py --no-cache       # forces live requests, ignoring the cache
```

Outputs are written to `output/books.json`, `output/errors.json`, and `output/run-report.json`.

---

## Sample Run Report

*[paste your actual `output/run-report.json` here as proof of a real run]*

```json
{
  "start_time": "...",
  "duration_seconds": 0,
  "catalogue_pages_crawled": 3,
  "pages_fetched": 0,
  "cache_hits": 0,
  "discovered_urls": 60,
  "unique_urls": 60,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 0,
  "inject_broken_used": false
}
```

---

## Why No Browser Was Needed

All the data used in this assignment (title, price, availability, rating, description) is already
present in the server-rendered HTML — there's no JavaScript-loaded content to wait for. Reaching
for a headless browser here would only add startup cost and complexity for no extra data.

---

## Tests

Unit tests live in `tests/test_scraper.py` and cover:
- Price text → numeric GBP normalization
- Relative → absolute URL conversion
- Missing description handled as `null`
- Duplicate URL removal
- One malformed HTML fixture

Run with:

```bash
pytest tests/
```

---

## Ethics Note

Books to Scrape is a public sandbox that exists specifically for scraping practice — no login,
paywall, or access control is bypassed. In a real project, an official API is preferred over
scraping whenever one exists, and only the data actually needed is collected.

---

## Known Limitation

*[one honest limitation of your implementation — e.g. retry logic is a single attempt on 5xx errors rather than full exponential backoff]*

---

## Bonus — AI Rematch

`ai-version/` contains an AI-generated implementation of the same specification, built in isolation
from the hand-built version above. See `ai-version/README.md` for the prompt used, checkpoint
results for both versions, and a comparison of what the AI did better, what it missed, and what the
original prompt failed to specify.