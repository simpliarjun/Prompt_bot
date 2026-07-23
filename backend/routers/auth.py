"""
Auth router — register, login, me.

§11 Auth API + §17 error handling.
Correction #13: UTC-aware timestamps.
Correction #14: structured logging on every error branch.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.concurrency import run_in_threadpool

from database import get_db
from dependencies import get_current_user
from logging_config import get_logger
from models.user import Token, UserCreate, UserLogin, UserResponse
from security import create_access_token, hash_password, verify_password

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=201)
async def register(body: UserCreate):
    db = get_db()

    # Check for duplicate email
    existing = await db.users.find_one({"email": body.email})
    if existing:
        logger.warning("Registration attempt with existing email")
        raise HTTPException(status_code=409, detail="Email already registered")

    now = datetime.now(timezone.utc)
    hashed_pwd = await run_in_threadpool(hash_password, body.password)
    user_doc = {
        "full_name": body.full_name,
        "email": body.email,
        "hashed_password": hashed_pwd,
        "created_at": now,
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    token = create_access_token(user_id)
    user_resp = UserResponse(
        id=user_id,
        full_name=body.full_name,
        email=body.email,
        created_at=now,
    )
    logger.info("User registered: %s", user_id)
    return Token(access_token=token, user=user_resp)


@router.post("/login", response_model=Token)
async def login(body: UserLogin):
    db = get_db()
    user_doc = await db.users.find_one({"email": body.email})

    if user_doc is None:
        logger.warning("Failed login attempt")
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    is_valid = await run_in_threadpool(verify_password, body.password, user_doc["hashed_password"])
    if not is_valid:
        logger.warning("Failed login attempt")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = str(user_doc["_id"])
    token = create_access_token(user_id)
    user_resp = UserResponse(
        id=user_id,
        full_name=user_doc["full_name"],
        email=user_doc["email"],
        created_at=user_doc["created_at"],
    )
    logger.info("User logged in: %s", user_id)
    return Token(access_token=token, user=user_resp)


@router.get("/me", response_model=UserResponse)
async def me(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@router.delete("/me", status_code=204, response_class=Response)
async def delete_me(current_user: UserResponse = Depends(get_current_user)):
    """
    Delete the current user and all associated grievances (Cascading Delete).
    """
    from database import to_object_id
    db = get_db()
    
    uid = to_object_id(current_user.id)
    
    # Delete all user's grievances
    grievances_result = await db.grievances.delete_many({"user_id": uid})
    logger.info("Deleted %d grievances for user %s", grievances_result.deleted_count, current_user.id)
    
    # Delete the user record
    await db.users.delete_one({"_id": uid})
    logger.info("Deleted user %s", current_user.id)
    
    return None
