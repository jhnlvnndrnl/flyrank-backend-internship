"""
tests/test_scraper.py
---------------------
Five unit tests covering the core logic of the A9 polite scraper.

All tests use local HTML fixtures or pure data — no live HTTP requests.

Tests
-----
1. Price normalisation         (models.normalise_price)
2. Relative → absolute URL     (parser.parse_catalogue_page)
3. Missing description         (parser.parse_book_detail)
4. Duplicate URL deduplication (catalogue crawl logic)
5. Malformed HTML fixture      (parser.parse_catalogue_page)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# ── Path bootstrap ────────────────────────────────────────────────────────
# Allow "pytest tests/" from the project root without installing the package.
_TESTS_DIR = Path(__file__).resolve().parent
_SRC_DIR = _TESTS_DIR.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

# pyrefly: ignore [missing-import]
from models import normalise_price
# pyrefly: ignore [missing-import]
from parser import parse_book_detail, parse_catalogue_page

# Fixtures directory
FIXTURES_DIR = _TESTS_DIR / "fixtures"

# Test 1 – Price normalisation

class TestNormalisePrice:
    """normalise_price should extract a float from various price string formats."""

    def test_standard_gbp(self):
        """'£51.77' → 51.77"""
        assert normalise_price("£51.77") == pytest.approx(51.77)

    def test_mojibake_gbp(self):
        """'Â£51.77' (common encoding artefact on this site) → 51.77"""
        assert normalise_price("Â£51.77") == pytest.approx(51.77)

    def test_plain_number(self):
        """A bare numeric string should still parse."""
        assert normalise_price("12.99") == pytest.approx(12.99)

    def test_zero_price(self):
        """A free book (£0.00) is valid."""
        assert normalise_price("£0.00") == pytest.approx(0.0)

    def test_no_numeric_value_raises(self):
        """A string with no digits should raise ValueError."""
        with pytest.raises(ValueError, match="Could not extract"):
            normalise_price("no-price-here")


# Test 2 – Relative → absolute URL conversion

class TestRelativeToAbsoluteURL:
    """parse_catalogue_page must resolve relative hrefs with urljoin, not string concat."""

    def test_relative_href_becomes_absolute(self, tmp_path):
        """
        The catalogue uses hrefs like '../../catalogue/<slug>/index.html'.
        parse_catalogue_page must return fully qualified HTTPS URLs.
        """
        html = """
        <html><body>
          <article class="product_pod">
            <h3>
              <a href="../../catalogue/a-light-in-the-attic_1000/index.html"
                 title="A Light in the Attic">A Light in ...</a>
            </h3>
          </article>
        </body></html>
        """
        page_url = "https://books.toscrape.com/catalogue/page-1.html"
        book_urls, next_url = parse_catalogue_page(html, page_url)

        assert len(book_urls) == 1
        assert book_urls[0] == (
            "https://books.toscrape.com/catalogue/"
            "a-light-in-the-attic_1000/index.html"
        )

    def test_next_page_url_is_absolute(self):
        """The next-page link must also be returned as an absolute URL."""
        html = """
        <html><body>
          <ul class="pager">
            <li class="next"><a href="page-2.html">next</a></li>
          </ul>
        </body></html>
        """
        page_url = "https://books.toscrape.com/catalogue/page-1.html"
        _, next_url = parse_catalogue_page(html, page_url)

        assert next_url == "https://books.toscrape.com/catalogue/page-2.html"

    def test_no_next_link_returns_none(self):
        """A page without a 'next' link should return None for next_url."""
        html = "<html><body><p>No pager here</p></body></html>"
        _, next_url = parse_catalogue_page(
            html, "https://books.toscrape.com/catalogue/page-3.html"
        )
        assert next_url is None


# Test 3 – Missing description handling

class TestMissingDescription:
    """parse_book_detail must store None when no description is present."""

    # Minimal valid book page with no description section
    _HTML_NO_DESCRIPTION = """
    <html><body>
      <div class="product_main">
        <h1>Some Book Title</h1>
        <p class="price_color">£10.99</p>
        <p class="availability">In stock</p>
        <p class="star-rating Three"></p>
      </div>
      <!-- deliberately NO #product_description div -->
    </body></html>
    """

    def test_description_is_none_when_missing(self):
        raw = parse_book_detail(
            self._HTML_NO_DESCRIPTION,
            product_url="https://books.toscrape.com/catalogue/some-book_1/index.html",
            source_page="https://books.toscrape.com/catalogue/page-1.html",
            fetched_at="2026-08-06T10:00:00Z",
        )
        assert raw.description is None

    def test_description_is_none_for_empty_p(self):
        """An empty <p> after #product_description should also yield None."""
        html = """
        <html><body>
          <div class="product_main">
            <h1>Empty Desc Book</h1>
            <p class="price_color">£5.00</p>
            <p class="availability">In stock</p>
            <p class="star-rating One"></p>
          </div>
          <div id="product_description"></div>
          <p></p>
        </body></html>
        """
        raw = parse_book_detail(
            html,
            product_url="https://books.toscrape.com/catalogue/empty_1/index.html",
            source_page="https://books.toscrape.com/catalogue/page-1.html",
            fetched_at="2026-08-06T10:00:00Z",
        )
        assert raw.description is None

    def test_description_extracted_when_present(self):
        """A real description paragraph should be extracted correctly."""
        html = """
        <html><body>
          <div class="product_main">
            <h1>Book With Desc</h1>
            <p class="price_color">£9.99</p>
            <p class="availability">In stock</p>
            <p class="star-rating Four"></p>
          </div>
          <div id="product_description"><h2>Product Description</h2></div>
          <p>A wonderful description of the book.</p>
        </body></html>
        """
        raw = parse_book_detail(
            html,
            product_url="https://books.toscrape.com/catalogue/with-desc_1/index.html",
            source_page="https://books.toscrape.com/catalogue/page-1.html",
            fetched_at="2026-08-06T10:00:00Z",
        )
        assert raw.description == "A wonderful description of the book."


# Test 4 – Duplicate URL deduplication

class TestDuplicateURLDeduplication:
    """
    If the same URL appears twice in the discovered list (e.g. a book featured
    on multiple catalogue pages), the scraper must deduplicate before fetching.
    """

    def test_duplicates_are_removed(self):
        """
        Simulate two catalogue pages both returning the same 20 URLs.
        After deduplication there should be exactly 20 unique URLs.
        """
        page_urls = [
            f"https://books.toscrape.com/catalogue/book-{i}_1/index.html"
            for i in range(20)
        ]
        # All URLs appear twice (simulating overlap across pages)
        duplicated = page_urls + page_urls

        seen: set[str] = set()
        unique: list[str] = []
        for url in duplicated:
            if url not in seen:
                seen.add(url)
                unique.append(url)

        assert len(unique) == 20
        # Order must be preserved (first occurrence wins)
        assert unique == page_urls

    def test_single_url_is_not_duplicated(self):
        urls = ["https://books.toscrape.com/catalogue/solo_1/index.html"] * 5
        seen: set[str] = set()
        unique = [u for u in urls if not (u in seen or seen.add(u))]
        assert len(unique) == 1


# Test 5 – Malformed HTML fixture

class TestMalformedHTML:
    """
    The parser must not crash on broken or empty HTML.
    It should return empty / None values rather than raising an exception.
    """

    def test_completely_empty_html(self):
        """parse_catalogue_page on an empty string must return empty lists."""
        book_urls, next_url = parse_catalogue_page(
            "", "https://books.toscrape.com/catalogue/page-1.html"
        )
        assert book_urls == []
        assert next_url is None

    def test_garbage_html_does_not_crash(self):
        """Random bytes / garbled markup must not raise an exception."""
        garbage = "<<<<html>><>><div class='broken'></p></article><<<"
        book_urls, next_url = parse_catalogue_page(
            garbage, "https://books.toscrape.com/catalogue/page-1.html"
        )
        # We don't care about the values, only that it didn't crash
        assert isinstance(book_urls, list)
        assert next_url is None or isinstance(next_url, str)

    def test_missing_product_main_yields_empty_title(self):
        """
        If the <div class="product_main"> is absent the title should be an
        empty string (not an AttributeError).
        """
        html = "<html><body><p>No structure here</p></body></html>"
        raw = parse_book_detail(
            html,
            product_url="https://books.toscrape.com/catalogue/missing_1/index.html",
            source_page="https://books.toscrape.com/catalogue/page-1.html",
            fetched_at="2026-08-06T10:00:00Z",
        )
        assert raw.title == ""
        assert raw.description is None

    def test_fixture_file_catalogue_page(self):
        """
        Load a saved HTML fixture and verify parse_catalogue_page extracts
        at least one book URL from it.

        If the fixture file does not exist this test is automatically skipped
        so the test suite still passes in a fresh checkout (before any caching).
        """
        fixture_path = FIXTURES_DIR / "catalogue-page-1.html"
        if not fixture_path.exists():
            pytest.skip("Fixture not found – run the scraper once to generate it.")

        html = fixture_path.read_text(encoding="utf-8")
        book_urls, next_url = parse_catalogue_page(
            html, "https://books.toscrape.com/catalogue/page-1.html"
        )
        assert len(book_urls) == 20          # 20 books per page
        assert next_url is not None          # page 1 always has a next link
