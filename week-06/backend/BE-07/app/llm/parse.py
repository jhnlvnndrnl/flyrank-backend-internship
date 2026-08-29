"""
BE-07 Parse & Validate — turns raw model text into trusted, schema-valid output.

The model is an external source. Its answer is raw input.
This module:
  1. Strips markdown fences and preamble to find the JSON object
  2. Validates against the Pydantic schema
  3. On failure: triggers one repair retry
  4. On second failure: returns None and logs to quarantine

Raw model text is NEVER returned to the caller.
"""

import json
import re
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

from app.llm.schema import EnrichmentResult

logger = logging.getLogger("be07.parse")

# Quarantine log directory
LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "logs"


def extract_json_from_text(text: str) -> Optional[str]:
    """
    Extract a JSON object from model output that may contain markdown fences,
    preamble text like "Sure! Here's the JSON:", or trailing commentary.

    Returns the extracted JSON string, or None if no JSON object was found.
    """
    if not text or not text.strip():
        return None

    text = text.strip()

    # Try 1: Strip markdown code fences (```json ... ``` or ``` ... ```)
    fence_pattern = r"```(?:json)?\s*\n?(.*?)\n?\s*```"
    fence_match = re.search(fence_pattern, text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()

    # Try 2: Find the first { ... } block (greedy from first { to last })
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        return brace_match.group(0).strip()

    return None


def validate_output(raw_text: str) -> Tuple[Optional[EnrichmentResult], Optional[str]]:
    """
    Parse and validate model output against the EnrichmentResult schema.

    Returns:
        (result, None) on success
        (None, error_message) on failure
    """
    json_str = extract_json_from_text(raw_text)
    if json_str is None:
        return None, "No JSON object found in model output."

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {e}"

    try:
        result = EnrichmentResult.model_validate(data)
        return result, None
    except Exception as e:
        return None, f"Schema validation failed: {e}"


def log_to_quarantine(
    input_text: str,
    raw_output: str,
    error: str,
    prompt_version: str,
    attempt: int,
) -> None:
    """
    Log a failed model output to logs/quarantine.jsonl.

    Bad output is set aside instead of crashing the run or reaching the database.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    quarantine_path = LOGS_DIR / "quarantine.jsonl"

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_version": prompt_version,
        "attempt": attempt,
        "input_preview": input_text[:200],
        "raw_output": raw_output,
        "error": error,
    }

    with open(quarantine_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    logger.warning(
        "Quarantined model output | prompt=%s attempt=%d error=%s",
        prompt_version, attempt, error,
    )


def build_repair_messages(
    original_messages: list,
    broken_output: str,
    validation_error: str,
) -> list:
    """
    Build messages for a repair retry: same prompt, plus the broken output
    and the exact validation error, plus a correction instruction.
    """
    repair_instruction = (
        f"Your previous answer was rejected for this reason:\n"
        f"---\n"
        f"Output: {broken_output}\n"
        f"Error: {validation_error}\n"
        f"---\n"
        f"Return only corrected JSON matching the schema. "
        f"No markdown fences, no explanation, just the JSON object."
    )

    return original_messages + [
        {"role": "assistant", "content": broken_output},
        {"role": "user", "content": repair_instruction},
    ]
