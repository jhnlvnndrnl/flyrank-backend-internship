"""
BE-07: LLM Integration — Enrich Scraped Records API

A production-grade endpoint that takes messy scraped content, sends it to an LLM,
and returns clean validated JSON with a real timeout, sensible retries, a cost log,
and a kill switch.

The model is a slow, clever, sometimes wrong external API — and you already
know how to handle one of those.

Author: John Elvin Endrenal
Week: 6 (BE-07 / A17)
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from openai import APITimeoutError, APIStatusError

from app.config import LLM_STUB, LLM_ENABLED, PORT, PROMPT_VERSION
from app.llm.schema import EnrichmentInput, EnrichmentResult, STUB_RESPONSE
from app.llm.prompt import load_prompt, build_messages
from app.llm.client import call_model, log_cost
from app.llm.parse import validate_output, log_to_quarantine, build_repair_messages

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("be07")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager logging server startup and configuration."""
    logger.info("Server starting on port %d", PORT)
    logger.info("LLM_STUB=%s | LLM_ENABLED=%s | PROMPT_VERSION=%s", LLM_STUB, LLM_ENABLED, PROMPT_VERSION)
    if LLM_STUB:
        logger.info("Stub mode active — model calls will be skipped")
    if not LLM_ENABLED:
        logger.info("Kill switch active — LLM_ENABLED=false, returning fallback")
    yield


app = FastAPI(
    title="BE-07: Enrich Scraped Records API",
    version="1.0.0",
    description=(
        "Takes messy scraped content, classifies it via an LLM, "
        "and returns clean validated JSON with timeout, retries, "
        "cost logging, and a kill switch."
    ),
    lifespan=lifespan,
)


# --- Exception Handlers ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Return 400 Bad Request for input validation failures, naming the offending field.
    Every rejected request is a model call you did not pay for.
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Validation failed", "details": errors},
    )


# --- Endpoints ---

@app.get("/", summary="API Root")
def get_root():
    """Root endpoint describing the API."""
    return {
        "name": "BE-07: Enrich Scraped Records API",
        "version": "1.0.0",
        "status": "online",
        "llm_enabled": LLM_ENABLED,
        "stub_mode": LLM_STUB,
        "prompt_version": PROMPT_VERSION,
    }


@app.post(
    "/enrich",
    status_code=status.HTTP_200_OK,
    response_model=EnrichmentResult,
    summary="Enrich a Scraped Record",
    description=(
        "Classifies and enriches a scraped web record with a standardized category, "
        "concise summary, and quality flags. Input is validated before any model call. "
        "Output is validated against the schema — if the model's answer fails validation, "
        "it gets one repair retry, then a 422."
    ),
)
async def enrich(payload: EnrichmentInput):
    """
    The whole endpoint in six lines:
      1. validate the input       → reject garbage before you spend a call
      2. build the prompt         → from a file, with a version number
      3. call the model           → with a timeout, and retries on the right errors only
      4. parse + validate output  → against the schema
      5. repair once if it failed → hand the model its own error message
      6. return clean JSON        → or a clear 422 — never raw model text
    """

    # --- STUB MODE: return hard-coded valid response, zero model calls ---
    if LLM_STUB:
        logger.info("Stub mode — returning hard-coded response")
        return STUB_RESPONSE

    # --- KILL SWITCH: LLM disabled, return deterministic fallback ---
    if not LLM_ENABLED:
        logger.info("Kill switch active — returning 503")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "LLM service is currently disabled",
                "fallback": STUB_RESPONSE.model_dump(),
            },
        )

    # --- LOAD PROMPT ---
    try:
        system_prompt = load_prompt(PROMPT_VERSION)
    except FileNotFoundError as e:
        logger.error("Prompt file not found: %s", e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Prompt file not found: {e}"},
        )

    messages = build_messages(system_prompt, payload.raw_text, payload.source_url)

    # --- CALL THE MODEL ---
    total_input_tokens = 0
    total_output_tokens = 0
    total_duration_ms = 0
    repair_count = 0

    try:
        response = call_model(messages)
    except APITimeoutError:
        logger.error("Model call timed out")
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={"error": "Model call timed out. Please try again later."},
        )
    except APIStatusError as e:
        logger.error("Model call failed: %s %s", e.status_code, e.message)
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"error": f"Model call failed with status {e.status_code}"},
        )
    except Exception as e:
        logger.error("Unexpected error calling model: %s", e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "An unexpected error occurred while calling the model."},
        )

    total_input_tokens += response["input_tokens"]
    total_output_tokens += response["output_tokens"]
    total_duration_ms += response["duration_ms"]

    # --- PARSE + VALIDATE ---
    result, error = validate_output(response["content"])

    # --- REPAIR ONCE if validation failed ---
    if result is None and error is not None:
        logger.warning("First attempt failed validation: %s", error)
        repair_count = 1

        # Log the first failure
        log_to_quarantine(
            input_text=payload.raw_text,
            raw_output=response["content"],
            error=error,
            prompt_version=PROMPT_VERSION,
            attempt=1,
        )

        # Build repair messages
        repair_messages = build_repair_messages(messages, response["content"], error)

        try:
            repair_response = call_model(repair_messages)
        except (APITimeoutError, APIStatusError, Exception) as e:
            logger.error("Repair call failed: %s", e)
            # Log cost for the first call even though we failed
            log_cost(PROMPT_VERSION, response["model"], total_input_tokens, total_output_tokens, total_duration_ms, repair_count)
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "error": "Model output failed validation and repair call also failed.",
                    "validation_error": error,
                },
            )

        total_input_tokens += repair_response["input_tokens"]
        total_output_tokens += repair_response["output_tokens"]
        total_duration_ms += repair_response["duration_ms"]

        # Validate the repaired output
        result, repair_error = validate_output(repair_response["content"])

        if result is None:
            # Second failure — quarantine and give up
            log_to_quarantine(
                input_text=payload.raw_text,
                raw_output=repair_response["content"],
                error=repair_error or "Unknown error",
                prompt_version=PROMPT_VERSION,
                attempt=2,
            )

            log_cost(PROMPT_VERSION, response["model"], total_input_tokens, total_output_tokens, total_duration_ms, repair_count)

            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "error": "Model output failed validation after one repair attempt.",
                    "validation_error": repair_error,
                },
            )

    # --- LOG COST ---
    log_cost(PROMPT_VERSION, response["model"], total_input_tokens, total_output_tokens, total_duration_ms, repair_count)

    # --- RETURN CLEAN JSON ---
    return result
