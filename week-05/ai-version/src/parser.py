"""
parser.py
---------
All BeautifulSoup HTML-parsing logic lives here.

Functions
---------
parse_catalogue_page(html, page_url)
    Returns (book_urls, next_page_url_or_None) for one catalogue page.

parse_book_detail(html, product_url, source_page)
    Returns a RawBook extracted from one book detail page.

Design notes
------------
* Every selector targets a meaningful element – not a fragile nth-child.
* Relative URLs are resolved with urllib.parse.urljoin (never string concat).
* If a field is missing from the HTML we store None; we never invent data.
"""

from __future__ import annotations

from typing import Optional
from urllib.parse import urljoin

# pyrefly: ignore [missing-import]
from bs4 import BeautifulSoup

from models import RawBook


# ---------------------------------------------------------------------------
# Catalogue page parsing
# ---------------------------------------------------------------------------

def parse_catalogue_page(
    html: str,
    page_url: str,
) -> tuple[list[str], Optional[str]]:
    """
    Parse one catalogue listing page.

    Parameters
    ----------
    html:
        Raw HTML of the catalogue page.
    page_url:
        The absolute URL of this catalogue page (used as base for urljoin).

    Returns
    -------
    book_urls:
        List of absolute book detail page URLs found on this page.
    next_url:
        Absolute URL of the next catalogue page, or None if this is the last.
    """
    soup = BeautifulSoup(html, "html.parser")

    # ── Book links ────────────────────────────────────────────────────────
    # Each book is inside an <article class="product_pod"> element.
    # The <h3><a href="..."> inside it contains the (possibly truncated) title
    # and the relative URL to the detail page.
    book_urls: list[str] = []
    for article in soup.select("article.product_pod"):
        anchor = article.select_one("h3 > a")
        if anchor and anchor.get("href"):
            relative_href: str = anchor["href"]
            # href is relative to the catalogue folder, e.g.
            # "../../catalogue/a-light-in-the-attic_1000/index.html"
            absolute_url = urljoin(page_url, relative_href)
            book_urls.append(absolute_url)

    # ── Next page link ────────────────────────────────────────────────────
    # The pager sits in <ul class="pager">; the "next" button is <li class="next">
    next_url: Optional[str] = None
    next_li = soup.select_one("li.next > a")
    if next_li and next_li.get("href"):
        next_url = urljoin(page_url, next_li["href"])

    return book_urls, next_url


# ---------------------------------------------------------------------------
# Book detail page parsing
# ---------------------------------------------------------------------------

# The word-to-number map for star ratings used on this site
_RATING_MAP: dict[str, int] = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


def parse_book_detail(
    html: str,
    product_url: str,
    source_page: str,
    fetched_at: str,
) -> RawBook:
    """
    Extract raw fields from one book detail page.

    Parameters
    ----------
    html:
        Raw HTML of the detail page.
    product_url:
        The absolute URL of this book (used to populate the RawBook).
    source_page:
        The catalogue page on which this book URL was discovered.
    fetched_at:
        ISO-8601 UTC timestamp of when the page was fetched.

    Returns
    -------
    RawBook with all eight fields populated (description may be None).
    """
    soup = BeautifulSoup(html, "html.parser")

    # ── Title ─────────────────────────────────────────────────────────────
    # The <div class="product_main"> contains the authoritative full title.
    product_main = soup.select_one("div.product_main")
    title: str = ""
    if product_main:
        h1 = product_main.select_one("h1")
        if h1:
            title = h1.get_text(strip=True)

    # ── Price ─────────────────────────────────────────────────────────────
    price_text: str = ""
    price_p = soup.select_one("p.price_color")
    if price_p:
        price_text = price_p.get_text(strip=True)

    # ── Availability ──────────────────────────────────────────────────────
    availability_text: str = ""
    avail_p = soup.select_one("p.availability")
    if avail_p:
        availability_text = avail_p.get_text(strip=True)

    # ── Rating ────────────────────────────────────────────────────────────
    # Rendered as <p class="star-rating Three"> – the second CSS class is the word.
    rating_text: str = ""
    rating_p = soup.select_one("p.star-rating")
    if rating_p:
        classes = rating_p.get("class", [])
        # classes = ["star-rating", "Three"]
        # Filter out the base class to get the word
        rating_words = [c for c in classes if c.lower() != "star-rating"]
        if rating_words:
            rating_text = rating_words[0]   # e.g. "Three"

    # ── Description ───────────────────────────────────────────────────────
    # The description lives in <div id="product_description"> followed by a <p>.
    # Some books genuinely have no description – in that case we store None.
    description: Optional[str] = None
    desc_header = soup.select_one("div#product_description")
    if desc_header:
        desc_p = desc_header.find_next_sibling("p")
        if desc_p:
            description = desc_p.get_text(strip=True) or None

    return RawBook(
        title=title,
        product_url=product_url,
        price_text=price_text,
        availability_text=availability_text,
        rating_text=rating_text,
        description=description,
        source_page=source_page,
        fetched_at=fetched_at,
    )
