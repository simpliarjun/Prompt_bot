"""
MongoDB-backed per-user rate limiter.

Correction #4: keyed on (user_id, UTC date) with a TTL index.
No slowapi, no Redis — works across horizontally scaled instances.
"""

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from database import get_db
from config import get_settings
from logging_config import get_logger

logger = get_logger(__name__)


async def check_and_increment(user_id: str) -> int:
    """
    Atomically check the user's generation count for today (UTC) and
    increment it.  Raises HTTP 429 if the daily limit is exceeded.

    Returns the new count after incrementing.
    """
    settings = get_settings()
    db = get_db()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Upsert: increment count, set expires_at on insert
    result = await db.rate_limits.find_one_and_update(
        {"user_id": user_id, "date": today},
        {
            "$inc": {"count": 1},
            "$setOnInsert": {
                "expires_at": datetime.now(timezone.utc) + timedelta(days=2),
            },
        },
        upsert=True,
        return_document=True,  # return the *after* document
    )

    current_count = result["count"]

    if current_count > settings.RATE_LIMIT_GENERATIONS_PER_DAY:
        logger.warning(
            "Rate limit exceeded for user %s: %d/%d",
            user_id,
            current_count,
            settings.RATE_LIMIT_GENERATIONS_PER_DAY,
        )
        raise HTTPException(
            status_code=429,
            detail=(
                f"Daily generation limit ({settings.RATE_LIMIT_GENERATIONS_PER_DAY}) "
                f"exceeded. Resets at midnight UTC."
            ),
        )

    return current_count
