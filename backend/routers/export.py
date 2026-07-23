"""
Export router — PDF export for grievances.

§11 Export API: GET /grievances/{id}/export/pdf
Correction #3: draft status → 400 (now reachable/testable).
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from database import doc_to_dict, get_db, to_object_id
from dependencies import get_current_user
from logging_config import get_logger
from models.user import UserResponse
from fastapi.concurrency import run_in_threadpool
from services.pdf_service import generate_pdf, get_pdf_filename

logger = get_logger(__name__)
router = APIRouter(prefix="/grievances", tags=["export"])


@router.get("/{grievance_id}/export/pdf")
async def export_pdf(
    grievance_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Export a grievance as a downloadable PDF.

    200 → application/pdf
    400 → grievance is still in draft status
    404 → not found or not owned by caller
    """
    db = get_db()
    oid = to_object_id(grievance_id)
    doc = await db.grievances.find_one(
        {"_id": oid, "user_id": to_object_id(current_user.id)}
    )

    if doc is None:
        raise HTTPException(status_code=404, detail="Grievance not found")

    if doc.get("status") == "draft":
        logger.info("PDF export blocked — grievance %s is still a draft", grievance_id)
        raise HTTPException(
            status_code=400,
            detail="Cannot export a draft grievance. Please save/finalize it first.",
        )

    grievance_dict = doc_to_dict(doc)
    pdf_bytes = await run_in_threadpool(generate_pdf, grievance_dict)
    filename = get_pdf_filename(grievance_dict)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
