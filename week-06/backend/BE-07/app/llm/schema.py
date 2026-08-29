"""
BE-07 Output Schema — defines the exact shape every response must match.

The model is an external source. Its answer is raw input.
These Pydantic models are the contract: if the model's output doesn't
pass validation here, it gets repaired once and then quarantined.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class CategoryEnum(str, Enum):
    """Closed list of allowed content categories."""
    PRODUCT = "product"
    BLOG = "blog"
    NEWS = "news"
    DOCUMENTATION = "documentation"
    JOB_LISTING = "job_listing"
    OTHER = "other"


class QualityFlagEnum(str, Enum):
    """Closed list of allowed quality flags."""
    INCOMPLETE = "incomplete"
    DUPLICATE = "duplicate"
    SPAM = "spam"
    LOW_QUALITY = "low_quality"
    FOREIGN_LANGUAGE = "foreign_language"


class EnrichmentInput(BaseModel):
    """Request body schema for POST /enrich."""
    raw_text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The scraped page content or record to classify and enrich (1–5000 characters).",
    )
    source_url: Optional[str] = Field(
        default=None,
        description="Optional URL the content was scraped from.",
    )


class EnrichmentResult(BaseModel):
    """
    Output schema — the exact JSON shape returned to the caller.
    Every category-like field is an enum. Nothing is free text except
    summary and reason, which the job card explicitly allows.
    """
    category: CategoryEnum = Field(
        ...,
        description="Content category from the closed list.",
    )
    summary: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="One or two sentence summary of the content.",
    )
    quality_flags: List[QualityFlagEnum] = Field(
        default_factory=list,
        description="Zero or more quality flags from the closed list.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0.",
    )
    reason: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="One short sentence explaining the classification.",
    )

    @field_validator("confidence")
    @classmethod
    def round_confidence(cls, v: float) -> float:
        """Round confidence to 2 decimal places for consistency."""
        return round(v, 2)


# Hard-coded stub response for LLM_STUB=1 mode
STUB_RESPONSE = EnrichmentResult(
    category=CategoryEnum.OTHER,
    summary="This is a stub response for development and testing purposes.",
    quality_flags=[],
    confidence=1.0,
    reason="Stub mode is active — no model was called.",
)
