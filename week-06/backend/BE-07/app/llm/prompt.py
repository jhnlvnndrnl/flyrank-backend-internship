"""
BE-07 Prompt Loader — loads the versioned prompt file and builds the messages array.

The prompt is a file, not a string in a route handler. It gets a version number,
goes through code review, and you can diff it when quality changes.
User-supplied content is sent as a separate user message — never concatenated
into the system prompt.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional


# Base directory for prompt files
PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"


def load_prompt(version: str = "v1") -> str:
    """
    Load the system prompt from prompts/enrich-{version}.md.

    Args:
        version: Prompt version string (e.g., "v1", "v2").

    Returns:
        The system prompt text.

    Raises:
        FileNotFoundError: If the prompt file doesn't exist.
    """
    prompt_path = PROMPTS_DIR / f"enrich-{version}.md"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def build_messages(
    system_prompt: str,
    raw_text: str,
    source_url: Optional[str] = None,
) -> List[Dict[str, str]]:
    """
    Build the messages array for the LLM call.

    The user's data is JSON-encoded and sent as a separate user message,
    never glued into the system prompt. Two reasons:
    1. The model treats roles differently.
    2. It keeps a wall between instructions and user content.

    Args:
        system_prompt: The loaded system prompt text.
        raw_text: The scraped content to classify.
        source_url: Optional source URL for context.

    Returns:
        List of message dicts ready for the OpenAI chat API.
    """
    # JSON-encode user content so it cannot break out of its own quotes
    # (basic prompt injection defence)
    user_payload = {"raw_text": raw_text}
    if source_url:
        user_payload["source_url"] = source_url

    user_message = json.dumps(user_payload, ensure_ascii=False)

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
