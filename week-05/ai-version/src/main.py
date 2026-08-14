"""
main.py
-------
Entry point for the FlyRank A9 "Polite Scraper".

Orchestration steps
-------------------
1.  Crawl exactly 3 catalogue pages following the site's own "next" links.
2.  Collect all book URLs (deduplicated).
3.  Fetch every book detail page (with caching and polite delays).
4.  Parse raw fields from each page.
5.  Normalise (price_text → price_gbp) and validate with Pydantic.
6.  Write books.json, errors.json, and run-report.json.

Usage
-----
    python src/main.py                  # normal run
    python src/main.py --inject-broken  # inject one fake URL to test failure handling
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

# Path bootstrap — allow "python src/main.py" from any working directory

_SRC_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SRC_DIR.parent

# Insert src/ at the front of sys.path so sibling modules are importable
# without installing the package.
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from models import Book, RawBook, ValidationError, normalise_price
from parser import parse_book_detail, parse_catalogue_page
from scraper import FetchError, fetch

# Configuration

CATALOGUE_START = "https://books.toscrape.com/catalogue/page-1.html"
MAX_CATALOGUE_PAGES = 3
OUTPUT_DIR = _PROJECT_ROOT / "output"

# A deliberately broken URL used only when --inject-broken is passed.
_BROKEN_URL = "https://books.toscrape.com/catalogue/this-book-does-not-exist_9999/index.html"


# Helpers

def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string with 'Z' suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_json(path: Path, data: object) -> None:
    """Write *data* to *path* as pretty-printed JSON (UTF-8)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  Wrote {path.relative_to(_PROJECT_ROOT)}")


# Step 1 – Crawl catalogue pages

def crawl_catalogue(
    session: requests.Session,
    *,
    use_cache: bool = True,
) -> tuple[list[str], int, int]:
    """
    Follow the site's "next" links for up to MAX_CATALOGUE_PAGES pages.

    Returns
    -------
    book_urls:
        Deduplicated list of absolute book detail page URLs.
    pages_fetched:
        Number of catalogue pages that were real HTTP requests.
    cache_hits:
        Number of catalogue pages served from the cache.
    """
    print("\n── Crawling catalogue pages ──────────────────────────────────────")

    all_book_urls: list[str] = []
    pages_fetched = 0
    cache_hits = 0
    current_url: Optional[str] = CATALOGUE_START

    for page_num in range(1, MAX_CATALOGUE_PAGES + 1):
        if current_url is None:
            print(f"  No more pages after page {page_num - 1}. Stopping.")
            break

        print(f"\n[Catalogue page {page_num}]  {current_url}")
        result = fetch(current_url, use_cache=use_cache, session=session)

        if result.cache_hit:
            cache_hits += 1
        else:
            pages_fetched += 1

        book_urls_on_page, next_url = parse_catalogue_page(
            result.html, current_url
        )
        print(f"  → Found {len(book_urls_on_page)} book links")
        all_book_urls.extend(book_urls_on_page)

        current_url = next_url if page_num < MAX_CATALOGUE_PAGES else None

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_urls: list[str] = []
    for url in all_book_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    print(f"\n  catalogue_pages={page_num}")
    print(f"  discovered={len(all_book_urls)}")
    print(f"  unique_urls={len(unique_urls)}")

    return unique_urls, pages_fetched, cache_hits


# Step 2 – Fetch and parse each book detail page

def process_books(
    book_urls: list[str],
    session: requests.Session,
    *,
    use_cache: bool = True,
) -> tuple[list[dict], list[dict], int, int, int]:
    """
    Fetch, parse, normalise, and validate each book detail page.

    Returns
    -------
    valid_records:
        List of plain dicts ready for books.json.
    error_records:
        List of plain dicts ready for errors.json.
    pages_fetched:
        Real HTTP requests made.
    cache_hits:
        Pages served from cache.
    failed_pages:
        Pages that could not be fetched at all.
    """
    print("\n── Processing book detail pages ──────────────────────────────────")

    valid_records: list[dict] = []
    error_records: list[dict] = []
    pages_fetched = 0
    cache_hits = 0
    failed_pages = 0

    total = len(book_urls)

    for idx, url in enumerate(book_urls, start=1):
        print(f"\n[{idx}/{total}] {url}")

        # ── Fetch ──────────────────────────────────────────────────────
        try:
            result = fetch(url, use_cache=use_cache, session=session)
        except FetchError as exc:
            print(f"  ERROR: {exc.reason}")
            error_records.append(
                ValidationError(
                    raw_data={"product_url": url},
                    reason=f"Fetch failed: {exc.reason}",
                ).to_dict()
            )
            failed_pages += 1
            continue

        if result.cache_hit:
            cache_hits += 1
        else:
            pages_fetched += 1

        # ── Parse ──────────────────────────────────────────────────────
        # We need to know which catalogue page this book was discovered on.
        # For simplicity we record the source as the canonical start URL of
        # the catalogue (the source_page field is a provenance hint, not a
        # guarantee of which page the scraper visited).
        fetched_at = _now_iso()
        try:
            raw: RawBook = parse_book_detail(
                result.html,
                product_url=url,
                source_page=CATALOGUE_START,  # provenance: started from page-1
                fetched_at=fetched_at,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"  PARSE ERROR: {exc}")
            error_records.append(
                ValidationError(
                    raw_data={"product_url": url},
                    reason=f"Parse failed: {exc}",
                ).to_dict()
            )
            failed_pages += 1
            continue

        # ── Normalise price ────────────────────────────────────────────
        try:
            price_gbp = normalise_price(raw.price_text)
        except ValueError as exc:
            print(f"  NORMALISE ERROR: {exc}")
            error_records.append(
                ValidationError(
                    raw_data=raw.model_dump(),
                    reason=f"Price normalisation failed: {exc}",
                ).to_dict()
            )
            continue

        # ── Validate with Pydantic ─────────────────────────────────────
        try:
            book = Book(
                title=raw.title,
                product_url=raw.product_url,
                price_text=raw.price_text,
                price_gbp=price_gbp,
                availability_text=raw.availability_text,
                rating_text=raw.rating_text,
                description=raw.description,
                source_page=raw.source_page,
                fetched_at=raw.fetched_at,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"  VALIDATION FAILED: {exc}")
            error_records.append(
                ValidationError(
                    raw_data=raw.model_dump(),
                    reason=str(exc),
                ).to_dict()
            )
            continue

        print(f"  ✓ {book.title!r}  £{book.price_gbp}")
        valid_records.append(book.to_dict())

    return valid_records, error_records, pages_fetched, cache_hits, failed_pages


# ---------------------------------------------------------------------------
# Step 3 – Idempotency merge
# ---------------------------------------------------------------------------

def merge_with_existing(
    new_records: list[dict],
    existing_path: Path,
) -> list[dict]:
    """
    Merge *new_records* with any previously saved records in *existing_path*.

    The canonical ``product_url`` field is used as the unique key.
    New records overwrite old ones with the same URL (in case we re-scraped
    with updated data), keeping the total at ≤ 60 unique entries.
    """
    existing: list[dict] = []
    if existing_path.exists():
        try:
            existing = json.loads(existing_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print("  WARNING: existing books.json is malformed – starting fresh.")

    # Build a dict keyed by product_url; new records overwrite old ones.
    merged: dict[str, dict] = {rec["product_url"]: rec for rec in existing}
    for rec in new_records:
        merged[rec["product_url"]] = rec

    return list(merged.values())


# Main orchestrator

def run(*, inject_broken: bool = False, use_cache: bool = True) -> None:
    start_time = time.time()
    start_iso = _now_iso()

    print("=" * 65)
    print("  FlyRank A9 – Polite Scraper")
    print(f"  Started : {start_iso}")
    print("=" * 65)

    session = requests.Session()
    session.headers.update({"Accept-Language": "en-GB,en;q=0.9"})

    # ── Step 1: Crawl catalogue pages ─────────────────────────────────
    unique_urls, cat_fetched, cat_cache = crawl_catalogue(
        session, use_cache=use_cache
    )

    # ── (Optional) inject a broken URL for testing ─────────────────────
    if inject_broken:
        print(f"\n  [TEST] Injecting broken URL: {_BROKEN_URL}")
        unique_urls.append(_BROKEN_URL)

    # ── Step 2: Process each book ─────────────────────────────────────
    valid_records, error_records, book_fetched, book_cache, failed_pages = (
        process_books(unique_urls, session, use_cache=use_cache)
    )

    # ── Step 3: Idempotency merge and write outputs ───────────────────
    books_path = OUTPUT_DIR / "books.json"
    errors_path = OUTPUT_DIR / "errors.json"
    report_path = OUTPUT_DIR / "run-report.json"

    print("\n── Writing outputs ───────────────────────────────────────────────")
    merged = merge_with_existing(valid_records, books_path)
    _write_json(books_path, merged)
    _write_json(errors_path, error_records)

    # ── Step 4: Run report ────────────────────────────────────────────
    duration = round(time.time() - start_time, 2)
    report = {
        "start_time": start_iso,
        "duration_seconds": duration,
        "catalogue_pages_crawled": MAX_CATALOGUE_PAGES,
        "pages_fetched": cat_fetched + book_fetched,
        "cache_hits": cat_cache + book_cache,
        "discovered_urls": len(unique_urls) - (1 if inject_broken else 0),
        "unique_urls": len(unique_urls) - (1 if inject_broken else 0),
        "valid_records": len(merged),
        "invalid_records": len(error_records),
        "failed_pages": failed_pages,
        "inject_broken_used": inject_broken,
    }
    _write_json(report_path, report)

    # ── Summary ───────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print(f"  Duration   : {duration}s")
    print(f"  Pages fetched (live)  : {report['pages_fetched']}")
    print(f"  Cache hits            : {report['cache_hits']}")
    print(f"  Valid records         : {report['valid_records']}")
    print(f"  Invalid / errors      : {report['invalid_records']}")
    print(f"  Failed pages          : {report['failed_pages']}")
    print("=" * 65)


# CLI entry point

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="FlyRank A9 – Polite Scraper for books.toscrape.com",
    )
    parser.add_argument(
        "--inject-broken",
        action="store_true",
        default=False,
        help=(
            "Add one deliberately broken book URL to test graceful failure "
            "handling.  The 60 valid records must survive."
        ),
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        default=False,
        help="Ignore and overwrite the cache (forces all live requests).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run(inject_broken=args.inject_broken, use_cache=not args.no_cache)
