"""
models.py
---------
Pydantic schema for a validated book record.

Raw fields come straight from the HTML.
Normalised fields (price_gbp) are derived during validation.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl, field_validator, model_validator


# ---------------------------------------------------------------------------
# Raw book (before validation / normalisation)
# ---------------------------------------------------------------------------

class RawBook(BaseModel):
    """
    Holds exactly what the parser extracted – no derived fields yet.
    All values are strings or None (as returned from BeautifulSoup).
    """

    title: str
    product_url: str          # may still be relative at this stage
    price_text: str           # e.g. "£51.77"
    availability_text: str    # e.g. "In stock (22 available)"
    rating_text: str          # e.g. "Three"
    description: Optional[str] = None
    source_page: str          # catalogue page the URL was found on
    fetched_at: str           # ISO-8601 UTC string, e.g. "2026-08-06T10:00:00Z"


# ---------------------------------------------------------------------------
# Validated + normalised book (what goes into books.json)
# ---------------------------------------------------------------------------

class Book(BaseModel):
    """
    Final validated book record.

    Constraints
    -----------
    * product_url  – must be an absolute HTTPS URL
    * price_gbp    – must be a positive float derived from price_text
    * title        – must not be empty
    """

    title: str
    product_url: HttpUrl                 # Pydantic validates the URL scheme
    price_text: str                      # original string preserved
    price_gbp: float                     # normalised numeric price
    availability_text: str
    rating_text: str
    description: Optional[str] = None   # null when missing – never invented
    source_page: str
    fetched_at: str

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be blank")
        return v.strip()

    @field_validator("price_text")
    @classmethod
    def price_text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("price_text must not be blank")
        return v.strip()

    @field_validator("price_gbp")
    @classmethod
    def price_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError(f"price_gbp must be non-negative, got {v}")
        return v

    @field_validator("fetched_at")
    @classmethod
    def fetched_at_valid_iso(cls, v: str) -> str:
        try:
            # Accept both "Z" suffix and "+00:00"
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(f"fetched_at is not a valid ISO-8601 string: {v!r}")
        return v

    # product_url is already validated as HttpUrl by Pydantic.
    # We add a cross-field check to make sure the scheme is HTTPS.
    @model_validator(mode="after")
    def url_must_be_https(self) -> "Book":
        url_str = str(self.product_url)
        if not url_str.startswith("https://"):
            raise ValueError(
                f"product_url must use HTTPS, got: {url_str!r}"
            )
        return self

    # ------------------------------------------------------------------
    # Serialisation helper
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Return a plain dict suitable for json.dumps."""
        d = self.model_dump()
        # HttpUrl is a Pydantic type; stringify it for plain JSON output.
        d["product_url"] = str(d["product_url"])
        return d


# ---------------------------------------------------------------------------
# Validation error record (what goes into errors.json)
# ---------------------------------------------------------------------------

class ValidationError(BaseModel):
    """Wraps a failed record together with the reason it failed."""

    raw_data: dict
    reason: str

    def to_dict(self) -> dict:
        return self.model_dump()


# ---------------------------------------------------------------------------
# Normalisation helper (used by main.py before constructing Book)
# ---------------------------------------------------------------------------

def normalise_price(price_text: str) -> float:
    """
    Extract the numeric GBP value from a price string.

    Examples
    --------
    "£51.77"  →  51.77
    "Â£51.77" →  51.77   (common mojibake on this site)
    "51.77"   →  51.77

    Raises
    ------
    ValueError  if no numeric value can be found
    """
    # Strip any leading currency symbols / encoding artefacts and whitespace
    cleaned = re.sub(r"[^\d.]", "", price_text)
    if not cleaned:
        raise ValueError(
            f"Could not extract a numeric price from {price_text!r}"
        )
    return float(cleaned)
