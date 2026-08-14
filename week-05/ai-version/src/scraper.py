"""
scraper.py
----------
Responsible for HTTP requests and simple file-based caching.

Design decisions
----------------
* One honest User-Agent on every real request.
* A 500 ms minimum delay between every real HTTP request (polite scraping).
* A configurable timeout (default: 10 s).
* Cache files are stored as plain HTML under cache/.
* Cache keys are derived from the URL so they are stable across runs.
* One retry (with a short back-off) on timeout or 5xx errors.
* No retry on 404 / 403 (that would be impolite or pointless).
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Optional

import requests

# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------

USER_AGENT: str = (
    "FlyRankInternship-A9/1.0 "
    "(+https://github.com/jhnlvnndrnl/flyrank-backend-internship)"
)

REQUEST_TIMEOUT: int = 10          # seconds
REQUEST_DELAY: float = 0.5         # seconds between real requests
RETRY_DELAY: float = 2.0           # seconds before one retry attempt

# Root of the project (two levels above this file: src/ → ai-version/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR: Path = _PROJECT_ROOT / "cache"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _cache_path_for(url: str) -> Path:
    """
    Derive a stable file-system-safe cache path from a URL.

    Strategy:
        1.  Use the URL path component as a human-readable prefix.
        2.  Append a short MD5 hash to guarantee uniqueness even when two
            URLs share the same path but differ in query string.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Remove scheme and host; keep only the path part
    stripped = url.split("://", 1)[-1]          # "books.toscrape.com/catalogue/page-2.html"
    stripped = stripped.split("?")[0]            # drop query string
    # Replace slashes and dots with dashes for a flat cache directory
    slug = stripped.replace("/", "-").replace(".", "-").strip("-")
    # Append a short hash to handle edge cases
    short_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    filename = f"{slug}-{short_hash}.html"
    return CACHE_DIR / filename


def _sleep(seconds: float) -> None:
    """Thin wrapper around time.sleep so it is easy to mock in tests."""
    time.sleep(seconds)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class FetchResult:
    """Simple container returned by fetch()."""

    __slots__ = ("html", "url", "cache_hit", "status_code")

    def __init__(
        self,
        html: str,
        url: str,
        *,
        cache_hit: bool,
        status_code: Optional[int] = None,
    ) -> None:
        self.html = html
        self.url = url
        self.cache_hit = cache_hit
        self.status_code = status_code   # None when served from cache


class FetchError(Exception):
    """Raised when a page cannot be fetched (all retries exhausted)."""

    def __init__(self, url: str, reason: str) -> None:
        self.url = url
        self.reason = reason
        super().__init__(f"Failed to fetch {url!r}: {reason}")


def fetch(url: str, *, use_cache: bool = True, session: Optional[requests.Session] = None) -> FetchResult:
    """
    Fetch ``url`` and return a FetchResult.

    Parameters
    ----------
    url:
        The absolute URL to fetch.
    use_cache:
        If True (default), look for a cached copy first and save the
        response to disk after a successful live request.
    session:
        An optional requests.Session.  Pass one from the caller so that
        connection pooling and headers are shared across many requests.

    Raises
    ------
    FetchError
        If the page cannot be retrieved after one retry.
    """
    cache_path = _cache_path_for(url)

    # ── 1. Cache hit ─────────────────────────────────────────────────────
    if use_cache and cache_path.exists():
        print(f"  CACHE HIT  {url}")
        return FetchResult(
            html=cache_path.read_text(encoding="utf-8", errors="replace"),
            url=url,
            cache_hit=True,
        )

    # ── 2. Live request (with one retry) ─────────────────────────────────
    headers = {"User-Agent": USER_AGENT}
    _session = session or requests.Session()

    def _do_request() -> requests.Response:
        return _session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)

    print(f"  FETCH      {url}")

    try:
        response = _do_request()
    except requests.exceptions.Timeout:
        # Retry once after a short back-off
        print(f"  TIMEOUT – retrying once … {url}")
        _sleep(RETRY_DELAY)
        try:
            response = _do_request()
        except requests.exceptions.RequestException as exc:
            raise FetchError(url, f"Timeout on retry: {exc}") from exc
    except requests.exceptions.RequestException as exc:
        raise FetchError(url, str(exc)) from exc

    # ── 3. Check status code ─────────────────────────────────────────────
    status = response.status_code

    if status == 404:
        raise FetchError(url, "HTTP 404 – page does not exist (no retry)")

    if status == 403:
        raise FetchError(url, "HTTP 403 – access forbidden (no retry, that would be impolite)")

    if status in range(500, 600):
        # Retry once for server errors
        print(f"  HTTP {status} – retrying once … {url}")
        _sleep(RETRY_DELAY)
        try:
            response = _do_request()
            status = response.status_code
        except requests.exceptions.RequestException as exc:
            raise FetchError(url, f"5xx then exception on retry: {exc}") from exc

        if status != 200:
            raise FetchError(url, f"HTTP {status} after retry")

    if status != 200:
        raise FetchError(url, f"Unexpected HTTP {status}")

    html = response.text

    # ── 4. Save to cache ─────────────────────────────────────────────────
    if use_cache:
        cache_path.write_text(html, encoding="utf-8")

    # ── 5. Polite delay before the caller can make the next request ───────
    _sleep(REQUEST_DELAY)

    return FetchResult(
        html=html,
        url=url,
        cache_hit=False,
        status_code=status,
    )
