"""
Motor async MongoDB client, connection helpers, and shared persistence utilities.

Centralises:
- Correction #1: incident_date  date ↔ datetime  conversion.
- Correction #2: user_id / _id  ObjectId ↔ str  conversion.
- Correction #5: Invalid ObjectId  → 404.
- Correction #8: Index creation (called from the lifespan handler in main.py).
"""

from datetime import date, datetime, time, timezone
from typing import Any, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config import get_settings
from logging_config import get_logger

logger = get_logger(__name__)

# Module-level references, set during app startup.
_client: Optional[AsyncIOMotorClient] = None  # type: ignore[type-arg]
_db: Optional[AsyncIOMotorDatabase] = None  # type: ignore[type-arg]


# ---------------------------------------------------------------------------
# Lifecycle helpers (called from main.py lifespan)
# ---------------------------------------------------------------------------

async def connect_db() -> None:
    """Open the Motor client and cache a database reference."""
    global _client, _db
    settings = get_settings()
    _client = AsyncIOMotorClient(settings.MONGODB_URI)
    _db = _client[settings.MONGODB_DB_NAME]
    # Quick connectivity check
    await _client.admin.command("ping")
    logger.info("Connected to MongoDB: %s", settings.MONGODB_DB_NAME)


async def close_db() -> None:
    """Close the Motor client."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB connection closed")


def get_db() -> AsyncIOMotorDatabase:  # type: ignore[type-arg]
    """FastAPI dependency — returns the cached database handle."""
    if _db is None:
        raise RuntimeError("Database not initialised — call connect_db() first")
    return _db


# ---------------------------------------------------------------------------
# Correction #8 — create §10 indexes idempotently on startup
# ---------------------------------------------------------------------------

async def create_indexes() -> None:
    """Create all required indexes. Safe to call repeatedly."""
    db = get_db()

    # users: unique email
    await db.users.create_index("email", unique=True)

    # grievances: per-user history sorted by date
    await db.grievances.create_index(
        [("user_id", 1), ("created_at", -1)],
        name="user_created_desc",
    )
    # grievances: per-user status filter
    await db.grievances.create_index(
        [("user_id", 1), ("status", 1)],
        name="user_status",
    )

    # rate_limits: TTL auto-cleanup (correction #4)
    await db.rate_limits.create_index(
        "expires_at",
        expireAfterSeconds=0,
        name="rate_limit_ttl",
    )

    logger.info("Database indexes ensured")


# ---------------------------------------------------------------------------
# Correction #2 / #5 — ObjectId helpers
# ---------------------------------------------------------------------------

def to_object_id(id_str: str) -> ObjectId:
    """
    Convert a string to a BSON ObjectId.
    Raises HTTP 404 if the string is not a valid ObjectId (correction #5).
    """
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Resource not found")


# ---------------------------------------------------------------------------
# Correction #1 — incident_date  date ↔ datetime
# ---------------------------------------------------------------------------

def date_to_datetime(d: date) -> datetime:
    """Convert a date to midnight-UTC datetime for BSON storage."""
    return datetime.combine(d, time.min, tzinfo=timezone.utc)


def datetime_to_date(dt: datetime) -> date:
    """Convert a stored datetime back to a plain date."""
    return dt.date()


# ---------------------------------------------------------------------------
# Document ↔ Pydantic helpers
# ---------------------------------------------------------------------------

def doc_to_dict(doc: dict[str, Any]) -> dict[str, Any]:
    """
    Prepare a raw MongoDB document for Pydantic model construction.

    - Renames ``_id`` → ``id`` and casts to ``str``.
    - Casts ``user_id`` to ``str`` (correction #2).
    - Converts ``incident_date`` datetime back to date (correction #1).
    """
    out = dict(doc)
    if "_id" in out:
        out["id"] = str(out.pop("_id"))
    if "user_id" in out and isinstance(out["user_id"], ObjectId):
        out["user_id"] = str(out["user_id"])
    if "incident_date" in out and isinstance(out["incident_date"], datetime):
        out["incident_date"] = datetime_to_date(out["incident_date"])
    return out
