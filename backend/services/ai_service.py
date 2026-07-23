"""
AI service — all Gemini prompt / config logic in one place (§6, §12).

Correction #10: Re-validate AI output server-side after parsing.
Correction #14: Structured logging on every error branch.
"""

import asyncio

from google import genai
from google.genai import types
from pydantic import ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config import get_settings
from logging_config import get_logger
from models.grievance import GeneratedGrievanceContent, GrievanceGenerateRequest

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Severity / SLA rubric — injected into the prompt template as a config dict
# so thresholds are tunable without editing prompt logic.
# ---------------------------------------------------------------------------

SEVERITY_SLA_RUBRIC: dict[str, dict[str, object]] = {
    "critical": {
        "hours": 24,
        "criteria": "safety/health risk, suspected fraud, ongoing or repeated harm",
    },
    "high": {
        "hours": 48,
        "criteria": "significant financial loss, breach of an explicit warranty/contract term",
    },
    "medium": {
        "hours": 120,
        "criteria": "standard product/service failure, first occurrence",
    },
    "low": {
        "hours": 168,
        "criteria": "minor inconvenience, cosmetic issue, limited-impact delay",
    },
}


def _build_rubric_text() -> str:
    lines = []
    for level, info in SEVERITY_SLA_RUBRIC.items():
        lines.append(f"    - {level} ({info['hours']}h): {info['criteria']}")
    return "\n".join(lines)


SYSTEM_INSTRUCTION = f"""\
You are an expert consumer-advocacy writing assistant for the Consumer Grievance
Management System (CGMS). Convert a consumer's raw account of a product or service
problem into a professional, factual, actionable formal complaint.

Rules:
1. Use ONLY facts provided in the input. Never invent dates, amounts, names, or events.
2. Tone: firm, clear, professional. Never aggressive, sarcastic, or emotionally charged,
   even if the customer's own words are.
3. Do NOT cite specific laws, statutes, regulations, or legal codes, and do not imply
   this letter is legal advice. General phrases like "reasonable expectations of
   quality" are fine; specific citations are not.
4. letter_body contains ONLY the body paragraphs — no salutation, no closing/signature
   (the application adds those). Structure: (a) one-sentence purpose statement,
   (b) factual account including all provided dates/references, (c) impact on the
   customer, (d) a specific statement of the desired resolution, (e) a professional
   request for a response within the suggested timeframe.
5. Classify severity and suggested_sla_hours using this rubric unless the facts clearly
   warrant deviation (explain any deviation in tone_note):
{_build_rubric_text()}
6. key_facts_summary: 3-6 short bullets a support agent could scan in five seconds.
"""


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class AIGenerationError(Exception):
    """Base error for AI generation failures."""


class AITimeoutError(AIGenerationError):
    """Gemini call timed out or had a transport error."""


class AISafetyBlockError(AIGenerationError):
    """Gemini safety-blocked the content (no candidates)."""


class AIMalformedOutputError(AIGenerationError):
    """Gemini returned output that didn't match the expected schema."""


from typing import Optional

# ---------------------------------------------------------------------------
# Client initialisation (lazy)
# ---------------------------------------------------------------------------

_client: Optional[genai.Client] = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        settings = get_settings()
        _client = genai.Client(api_key=settings.GEMINI_API_KEY.get_secret_value())
    return _client


def reset_client() -> None:
    """Reset the cached client (useful for tests)."""
    global _client
    _client = None


# ---------------------------------------------------------------------------
# Core generation function
# ---------------------------------------------------------------------------


@retry(
    retry=retry_if_exception_type((AIMalformedOutputError, AITimeoutError)),
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    reraise=True,
)
async def generate_grievance_letter(
    payload: GrievanceGenerateRequest,
) -> GeneratedGrievanceContent:
    """
    Call Gemini to generate a grievance letter from the user's input.

    Retries once on malformed output (correction #10).
    Raises typed AIGenerationError subclasses for the route to handle.
    """
    settings = get_settings()
    client = _get_client()

    prompt = (
        f"Company: {payload.company_name}\n"
        f"Product/Service: {payload.product_or_service}\n"
        f"Category: {payload.category.value}\n"
        f"Incident date: {payload.incident_date.isoformat()}\n"
        f"Order/Reference: {payload.order_reference or 'N/A'}\n"
        f"Desired resolution: {payload.desired_resolution.value}"
        f" — {payload.desired_resolution_details or ''}\n\n"
        f'Customer\'s own words:\n"""{payload.raw_description}"""'
    )

    try:
        response = await client.aio.models.generate_content(
            model=settings.GEMINI_MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=GeneratedGrievanceContent,
                temperature=0.4,
            ),
        )
    except asyncio.TimeoutError:
        logger.error("Gemini call timed out")
        raise AITimeoutError("The AI service timed out — please try again")
    except Exception as exc:
        logger.error("Gemini transport error: %s", exc)
        raise AITimeoutError(f"AI service error: {exc}") from exc

    # Safety block — no candidates
    if response.parsed is None:
        if response.candidates and any(
            c.finish_reason and "SAFETY" in str(c.finish_reason)
            for c in response.candidates
        ):
            logger.warning("Gemini safety-blocked the content")
            raise AISafetyBlockError(
                "Your description may contain content that needs rewording. "
                "Please revise and try again."
            )
        logger.warning("Gemini returned no parsable content")
        raise AIMalformedOutputError("AI returned no parsable content")

    parsed = response.parsed

    # Correction #10: re-validate server-side (Gemini's response_schema
    # doesn't reliably enforce minItems/maxItems for arrays).
    try:
        validated = GeneratedGrievanceContent.model_validate(parsed.model_dump())
    except ValidationError as exc:
        logger.warning("Gemini output failed re-validation: %s", exc)
        raise AIMalformedOutputError(
            f"AI output failed validation: {exc}"
        ) from exc

    # Extra check for key_facts_summary length
    if not (3 <= len(validated.key_facts_summary) <= 6):
        logger.warning(
            "key_facts_summary has %d items (expected 3-6)",
            len(validated.key_facts_summary),
        )
        raise AIMalformedOutputError(
            f"AI returned {len(validated.key_facts_summary)} key facts (expected 3-6)"
        )

    return validated
