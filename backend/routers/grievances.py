"""
Grievances router — full CRUD + stats endpoint.

Correction #1: incident_date conversion at persistence boundary.
Correction #2: user_id stored as ObjectId, serialized as str.
Correction #3: drafts savable via explicit status on create.
Correction #5: invalid ObjectId → 404.
Correction #7: GET /grievances/stats.
Correction #13: UTC-aware timestamps.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from database import date_to_datetime, doc_to_dict, get_db, to_object_id
from dependencies import PaginationParams, get_current_user
from logging_config import get_logger
from models.grievance import (
    GrievanceCategory,
    GrievanceCreateRequest,
    GrievanceResponse,
    GrievanceStatsResponse,
    GrievanceStatus,
    GrievanceUpdateRequest,
    PaginatedGrievanceResponse,
)
from models.user import UserResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/grievances", tags=["grievances"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_grievance_doc(
    body: GrievanceCreateRequest, user_id: str
) -> dict:
    """Build a MongoDB document from the create request."""
    now = datetime.now(timezone.utc)
    return {
        "user_id": to_object_id(user_id),
        "company_name": body.company_name,
        "product_or_service": body.product_or_service,
        "category": body.category.value,
        "incident_date": date_to_datetime(body.incident_date),  # correction #1
        "order_reference": body.order_reference,
        "raw_description": body.raw_description,
        "desired_resolution": body.desired_resolution.value,
        "desired_resolution_details": body.desired_resolution_details,
        "contact_name": body.contact_name,
        "contact_email": body.contact_email,
        "contact_phone": body.contact_phone,
        "subject_line": body.subject_line,
        "letter_body": body.letter_body,
        "key_facts_summary": body.key_facts_summary,
        "severity": body.severity.value,
        "suggested_sla_hours": body.suggested_sla_hours,
        "status": body.status.value,
        "created_at": now,
        "updated_at": now,
    }


# ---------------------------------------------------------------------------
# Stats (correction #7) — declared BEFORE /{id} to avoid path conflict
# ---------------------------------------------------------------------------


@router.get("/stats", response_model=GrievanceStatsResponse)
async def get_stats(
    current_user: UserResponse = Depends(get_current_user),
):
    """Return grievance counts by status via a single aggregation."""
    db = get_db()
    pipeline = [
        {"$match": {"user_id": to_object_id(current_user.id)}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    ]
    cursor = db.grievances.aggregate(pipeline)
    counts: dict[str, int] = {}
    async for doc in cursor:
        counts[doc["_id"]] = doc["count"]

    total = sum(counts.values())
    return GrievanceStatsResponse(
        draft=counts.get("draft", 0),
        finalized=counts.get("finalized", 0),
        sent=counts.get("sent", 0),
        resolved=counts.get("resolved", 0),
        escalated=counts.get("escalated", 0),
        total=total,
    )


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


@router.post("", response_model=GrievanceResponse, status_code=201)
async def create_grievance(
    body: GrievanceCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    db = get_db()
    doc = _build_grievance_doc(body, current_user.id)
    result = await db.grievances.insert_one(doc)
    doc["_id"] = result.inserted_id

    logger.info("Grievance created: %s (user %s)", result.inserted_id, current_user.id)
    return GrievanceResponse(**doc_to_dict(doc))


@router.get("", response_model=PaginatedGrievanceResponse)
async def list_grievances(
    pagination: PaginationParams = Depends(),
    status: Optional[GrievanceStatus] = Query(None),
    category: Optional[GrievanceCategory] = Query(None),
    current_user: UserResponse = Depends(get_current_user),
):
    db = get_db()
    query: dict = {"user_id": to_object_id(current_user.id)}
    if status:
        query["status"] = status.value
    if category:
        query["category"] = category.value

    total = await db.grievances.count_documents(query)
    cursor = (
        db.grievances.find(query)
        .sort("created_at", -1)
        .skip(pagination.skip)
        .limit(pagination.page_size)
    )
    items = [GrievanceResponse(**doc_to_dict(doc)) async for doc in cursor]

    return PaginatedGrievanceResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/{grievance_id}", response_model=GrievanceResponse)
async def get_grievance(
    grievance_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    db = get_db()
    oid = to_object_id(grievance_id)  # correction #5
    doc = await db.grievances.find_one(
        {"_id": oid, "user_id": to_object_id(current_user.id)}
    )
    if doc is None:
        raise HTTPException(status_code=404, detail="Grievance not found")
    return GrievanceResponse(**doc_to_dict(doc))


@router.put("/{grievance_id}", response_model=GrievanceResponse)
async def update_grievance(
    grievance_id: str,
    body: GrievanceUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    db = get_db()
    oid = to_object_id(grievance_id)
    user_oid = to_object_id(current_user.id)

    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=422, detail="No fields to update")

    # Convert enum to value string for storage
    if "status" in update_data and update_data["status"] is not None:
        update_data["status"] = update_data["status"].value

    update_data["updated_at"] = datetime.now(timezone.utc)

    result = await db.grievances.find_one_and_update(
        {"_id": oid, "user_id": user_oid},
        {"$set": update_data},
        return_document=True,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Grievance not found")

    logger.info("Grievance updated: %s", grievance_id)
    return GrievanceResponse(**doc_to_dict(result))


@router.delete("/{grievance_id}", status_code=204)
async def delete_grievance(
    grievance_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    db = get_db()
    oid = to_object_id(grievance_id)
    result = await db.grievances.delete_one(
        {"_id": oid, "user_id": to_object_id(current_user.id)}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Grievance not found")
    logger.info("Grievance deleted: %s", grievance_id)
