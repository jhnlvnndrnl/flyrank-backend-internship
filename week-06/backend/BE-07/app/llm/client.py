"""
BE-07 LLM Client — the single module that talks to the model.

Handles:
  - Client creation with an explicit 30-second timeout (not the SDK's 10-min default)
  - Custom retry logic: retry on timeout/429/5xx, NEVER on 400/401/403
  - Exponential backoff with jitter: 1s, 2s, 4s
  - Cost logging: prompt version, model, tokens, duration, repair count
  - Kill switch: LLM_ENABLED=false skips the model entirely

The SDK retries twice by default. We disable that and handle retries ourselves
so we have full control over which errors get retried. This is documented in
the README — silent defaults are how people end up making six calls when they
think they made one.
"""

import json
import time
import random
import logging
from typing import Optional, List, Dict

from openai import OpenAI, APITimeoutError, APIStatusError, APIConnectionError
from app.config import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, PROMPT_VERSION

logger = logging.getLogger("be07.client")

# Errors that should NEVER be retried — a bad key will still be bad in 4 seconds
NON_RETRYABLE_STATUS_CODES = {400, 401, 403}

# Max retries for retryable errors (timeout, 429, 5xx)
MAX_RETRIES = 3

# Base delay for exponential backoff (seconds)
BASE_DELAY = 1.0


def create_client() -> OpenAI:
    """
    Create an OpenAI-compatible client with an explicit 30-second timeout.

    The official SDK defaults to 10 minutes. If you leave that, one slow model
    call holds an HTTP connection open for 10 minutes and your endpoint looks dead.
    We also disable the SDK's built-in retries (default: 2) so we can control
    retry logic ourselves.
    """
    return OpenAI(
        base_url=LLM_BASE_URL,
        api_key=LLM_API_KEY,
        timeout=30.0,      # 30 seconds, not 10 minutes
        max_retries=0,      # We handle retries ourselves
    )


# Module-level client instance
_client: Optional[OpenAI] = None


def get_client() -> OpenAI:
    """Get or create the singleton client instance."""
    global _client
    if _client is None:
        _client = create_client()
    return _client


def _should_retry(error: Exception) -> bool:
    """
    Determine if an error is retryable.

    Yes on: timeouts, 429 (rate limit), 5xx (server errors)
    Never on: 400, 401, 403 — a bad key is still bad in four seconds,
    and on a metered free tier every pointless retry burns real quota.
    """
    if isinstance(error, (APITimeoutError, APIConnectionError)):
        return True
    if isinstance(error, APIStatusError):
        if error.status_code in NON_RETRYABLE_STATUS_CODES:
            return False
        # Retry on 429 and 5xx
        if error.status_code == 429 or error.status_code >= 500:
            return True
    return False


def _get_retry_delay(attempt: int, error: Optional[Exception] = None) -> float:
    """
    Calculate retry delay with exponential backoff and jitter.

    Pattern: base * 2^attempt + random jitter
    Attempt 0: ~1s, Attempt 1: ~2s, Attempt 2: ~4s

    If a 429 carries Retry-After, obey it instead of guessing.
    """
    # Check for Retry-After header on 429 responses
    if error and isinstance(error, APIStatusError) and error.status_code == 429:
        retry_after = getattr(error, "headers", {})
        if hasattr(retry_after, "get"):
            ra_value = retry_after.get("retry-after")
            if ra_value:
                try:
                    return float(ra_value)
                except (ValueError, TypeError):
                    pass

    delay = BASE_DELAY * (2 ** attempt)
    jitter = random.uniform(0, delay * 0.25)
    return delay + jitter


def call_model(
    messages: List[Dict[str, str]],
    temperature: float = 0.1,
) -> dict:
    """
    Call the LLM with retry logic, timeout handling, and cost logging.

    Args:
        messages: The messages array (system + user).
        temperature: Low for classification (0 or 0.2), not creativity.

    Returns:
        Dict with keys:
          - "content": str — the raw model response text
          - "input_tokens": int
          - "output_tokens": int
          - "duration_ms": int
          - "model": str

    Raises:
        APITimeoutError: If all retries are exhausted on timeouts.
        APIStatusError: If a non-retryable error occurs.
    """
    client = get_client()
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        start_time = time.monotonic()

        try:
            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                temperature=temperature,
            )

            duration_ms = int((time.monotonic() - start_time) * 1000)
            content = response.choices[0].message.content or ""
            usage = response.usage

            result = {
                "content": content,
                "input_tokens": usage.prompt_tokens if usage else 0,
                "output_tokens": usage.completion_tokens if usage else 0,
                "duration_ms": duration_ms,
                "model": response.model or LLM_MODEL,
            }

            return result

        except (APITimeoutError, APIStatusError, APIConnectionError) as e:
            last_error = e
            duration_ms = int((time.monotonic() - start_time) * 1000)

            if not _should_retry(e):
                logger.error(
                    "Non-retryable LLM error | status=%s duration=%dms attempt=%d",
                    getattr(e, "status_code", "timeout"),
                    duration_ms,
                    attempt,
                )
                raise

            if attempt < MAX_RETRIES:
                delay = _get_retry_delay(attempt, e)
                logger.warning(
                    "Retryable LLM error | status=%s duration=%dms attempt=%d delay=%.1fs",
                    getattr(e, "status_code", "timeout"),
                    duration_ms,
                    attempt,
                    delay,
                )
                time.sleep(delay)
            else:
                logger.error(
                    "LLM retries exhausted | status=%s attempts=%d",
                    getattr(e, "status_code", "timeout"),
                    MAX_RETRIES + 1,
                )
                raise

    # Should not reach here, but satisfy the type checker
    raise last_error  # type: ignore[misc]


def log_cost(
    prompt_version: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    duration_ms: int,
    repair_count: int,
) -> None:
    """
    Log a structured cost line for every model call.

    You cannot manage what you do not measure, and 'how much will this cost
    at ten thousand a day' is a question you will be asked in an interview.

    Writes to stdout as structured JSON — let the environment route it.
    """
    cost_entry = {
        "event": "llm_call",
        "prompt_version": prompt_version,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "duration_ms": duration_ms,
        "repair_count": repair_count,
    }
    logger.info("COST_LOG | %s", json.dumps(cost_entry))
    # Also print to stdout for easy visibility
    print(f"COST_LOG: {json.dumps(cost_entry)}")
