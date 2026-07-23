"""
FastAPI dependencies: current-user extraction, pagination params, ObjectId validation.
"""

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database import get_db, to_object_id
from logging_config import get_logger
from models.user import UserResponse
from security import decode_access_token

logger = get_logger(__name__)

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> UserResponse:
    """
    Extract and validate the JWT from the Authorization header.
    Returns a UserResponse; raises 401 on any failure.
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    db = get_db()
    oid = to_object_id(user_id)
    user_doc = await db.users.find_one({"_id": oid})
    if user_doc is None:
        raise HTTPException(status_code=401, detail="User not found")

    return UserResponse(
        id=str(user_doc["_id"]),
        full_name=user_doc["full_name"],
        email=user_doc["email"],
        created_at=user_doc["created_at"],
    )


class PaginationParams:
    """Dependency for paginated list endpoints."""

    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=10, ge=1, le=50),
    ):
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size
