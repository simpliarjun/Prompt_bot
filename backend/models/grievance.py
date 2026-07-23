"""
Grievance data models — §9.

Includes all enums, request/response schemas, and:
- Correction #6: GrievanceCreateRequest
- Correction #7: GrievanceStatsResponse
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------- Enums ----------


class GrievanceCategory(str, Enum):
    PRODUCT_DEFECT = "product_defect"
    SERVICE_FAILURE = "service_failure"
    BILLING_DISPUTE = "billing_dispute"
    DELIVERY_ISSUE = "delivery_issue"
    REFUND_REQUEST = "refund_request"
    WARRANTY_CLAIM = "warranty_claim"
    DATA_PRIVACY = "data_privacy"
    OTHER = "other"


class DesiredResolution(str, Enum):
    REFUND = "refund"
    REPLACEMENT = "replacement"
    REPAIR = "repair"
    APOLOGY = "apology"
    COMPENSATION = "compensation"
    CONTRACT_CANCELLATION = "contract_cancellation"
    OTHER = "other"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GrievanceStatus(str, Enum):
    DRAFT = "draft"
    FINALIZED = "finalized"
    SENT = "sent"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


# ---------- What the user submits to /api/generate ----------


class GrievanceGenerateRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    product_or_service: str = Field(..., min_length=1, max_length=200)
    category: GrievanceCategory
    incident_date: date
    order_reference: Optional[str] = Field(None, max_length=100)
    raw_description: str = Field(
        ...,
        min_length=10,
        max_length=4000,
        description="The user's raw, unfiltered account of what happened",
    )
    desired_resolution: DesiredResolution
    desired_resolution_details: Optional[str] = Field(None, max_length=500)
    contact_name: str = Field(..., max_length=150)
    contact_email: EmailStr
    contact_phone: Optional[str] = Field(None, max_length=30)


# ---------- The exact schema handed to Gemini as response_schema ----------


class GeneratedGrievanceContent(BaseModel):
    subject_line: str = Field(..., description="Concise, professional subject line")
    letter_body: str = Field(
        ...,
        description=(
            "Body paragraphs ONLY — no salutation, no closing/signature. "
            "The app template adds 'Dear {company} Customer Relations Team,' before "
            "and 'Sincerely,' after."
        ),
    )
    key_facts_summary: list[str] = Field(
        ...,
        min_length=3,
        max_length=6,
        description="Bullet points a support agent could scan in five seconds",
    )
    severity: SeverityLevel
    suggested_sla_hours: int = Field(..., gt=0, le=336)
    tone_note: Optional[str] = Field(
        None,
        description="Only set if severity/SLA deviates from the standard rubric — explain why",
    )


# ---------- Correction #6: POST /grievances request body ----------


class GrievanceCreateRequest(BaseModel):
    """
    All fields from GrievanceGenerateRequest (the user's original input) plus
    the AI-generated fields, plus optional status.
    """

    # --- User input fields ---
    company_name: str = Field(..., min_length=1, max_length=200)
    product_or_service: str = Field(..., min_length=1, max_length=200)
    category: GrievanceCategory
    incident_date: date
    order_reference: Optional[str] = Field(None, max_length=100)
    raw_description: str = Field(..., min_length=10, max_length=4000)
    desired_resolution: DesiredResolution
    desired_resolution_details: Optional[str] = Field(None, max_length=500)
    contact_name: str = Field(..., max_length=150)
    contact_email: EmailStr
    contact_phone: Optional[str] = Field(None, max_length=30)

    # --- AI-generated fields ---
    subject_line: str = Field(..., min_length=1)
    letter_body: str = Field(..., min_length=1)
    key_facts_summary: list[str] = Field(..., min_length=1)
    severity: SeverityLevel
    suggested_sla_hours: int = Field(..., gt=0, le=336)

    # --- Correction #3: status is optional, default finalized, only draft|finalized on create ---
    status: GrievanceStatus = Field(default=GrievanceStatus.FINALIZED)

    @field_validator("status")
    @classmethod
    def validate_create_status(cls, v: GrievanceStatus) -> GrievanceStatus:
        allowed = {GrievanceStatus.DRAFT, GrievanceStatus.FINALIZED}
        if v not in allowed:
            raise ValueError(
                f"Status on create must be 'draft' or 'finalized', got '{v.value}'"
            )
        return v


# ---------- Persisted document shape ----------


class GrievanceDB(BaseModel):
    id: str
    user_id: str
    company_name: str
    product_or_service: str
    category: GrievanceCategory
    incident_date: date
    order_reference: Optional[str] = None
    raw_description: str
    desired_resolution: DesiredResolution
    desired_resolution_details: Optional[str] = None
    contact_name: str
    contact_email: EmailStr
    contact_phone: Optional[str] = None

    subject_line: str
    letter_body: str
    key_facts_summary: list[str]
    severity: SeverityLevel
    suggested_sla_hours: int

    status: GrievanceStatus = GrievanceStatus.DRAFT
    created_at: datetime
    updated_at: datetime


class GrievanceResponse(GrievanceDB):
    """What the API returns — identical shape to GrievanceDB for v1."""

    pass


class GrievanceUpdateRequest(BaseModel):
    subject_line: Optional[str] = None
    letter_body: Optional[str] = None
    status: Optional[GrievanceStatus] = None


# ---------- Paginated response ----------


class PaginatedGrievanceResponse(BaseModel):
    items: list[GrievanceResponse]
    total: int
    page: int
    page_size: int


# ---------- Correction #7: Stats response ----------


class GrievanceStatsResponse(BaseModel):
    draft: int = 0
    finalized: int = 0
    sent: int = 0
    resolved: int = 0
    escalated: int = 0
    total: int = 0
