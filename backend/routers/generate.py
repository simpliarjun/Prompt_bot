"""
Generate router — POST /generate.

Calls the Gemini AI to produce a grievance letter draft.
Rate-limited per user (correction #4).
"""

from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_current_user
from logging_config import get_logger
from models.grievance import GeneratedGrievanceContent, GrievanceGenerateRequest
from models.user import UserResponse
from services.ai_service import (
    AIGenerationError,
    AIMalformedOutputError,
    AISafetyBlockError,
    AITimeoutError,
    generate_grievance_letter,
)
from services.rate_limiter import check_and_increment

logger = get_logger(__name__)
router = APIRouter(prefix="/generate", tags=["generate"])


class GenerateResponse(GeneratedGrievanceContent):
    """Wraps the AI output — returned inside { input, generated }."""

    pass


@router.post("")
async def generate(
    body: GrievanceGenerateRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Generate a grievance letter via Gemini.

    200 → { input: echo, generated: GeneratedGrievanceContent }
    422 → validation error
    429 → rate limit exceeded
    502 → AI service failure
    """
    # Rate limit check (correction #4)
    await check_and_increment(current_user.id)

    try:
        generated = await generate_grievance_letter(body)
    except AISafetyBlockError as exc:
        logger.warning("Safety block for user %s: %s", current_user.id, exc)
        raise HTTPException(status_code=502, detail=str(exc))
    except AITimeoutError as exc:
        logger.error("AI timeout for user %s: %s", current_user.id, exc)
        raise HTTPException(
            status_code=502,
            detail="The AI service is temporarily unavailable. Your input has been preserved — please try again.",
        )
    except AIMalformedOutputError as exc:
        logger.error("Malformed AI output for user %s: %s", current_user.id, exc)
        raise HTTPException(
            status_code=502,
            detail="The AI returned an unexpected response. Please try again.",
        )
    except AIGenerationError as exc:
        logger.error("AI generation error for user %s: %s", current_user.id, exc)
        raise HTTPException(status_code=502, detail=str(exc))

    return {
        "input": body.model_dump(mode="json"),
        "generated": generated.model_dump(mode="json"),
    }
