"""
Throwaway script to test AI service against the real Gemini API once.
This is the ONLY permitted real API call.

Usage:
    GEMINI_API_KEY=your-key python scripts/test_ai_service.py
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Must set env vars before importing app modules
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-for-script-only")
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")

from models.grievance import GrievanceGenerateRequest
from services.ai_service import generate_grievance_letter


async def main():
    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: Set GEMINI_API_KEY env var before running this script.")
        sys.exit(1)

    payload = GrievanceGenerateRequest(
        company_name="Acme Electronics",
        product_or_service="Wireless Headphones - Model X200",
        category="product_defect",
        incident_date="2026-07-10",
        order_reference="ORD-88213",
        raw_description=(
            "I purchased these headphones two weeks ago and they completely "
            "stopped working. The left ear has no sound at all, and the "
            "Bluetooth keeps disconnecting. I called customer support three "
            "times and was transferred around without any resolution. This "
            "is very frustrating as the product was expensive."
        ),
        desired_resolution="replacement",
        desired_resolution_details="A working replacement unit",
        contact_name="Asha Verma",
        contact_email="asha@example.com",
        contact_phone="+91-9876543210",
    )

    print("Calling Gemini API…")
    try:
        result = await generate_grievance_letter(payload)
        print("\n✅ SUCCESS!\n")
        print(f"Subject: {result.subject_line}")
        print(f"Severity: {result.severity.value}")
        print(f"SLA: {result.suggested_sla_hours}h")
        print(f"\nKey Facts ({len(result.key_facts_summary)}):")
        for fact in result.key_facts_summary:
            print(f"  • {fact}")
        print(f"\nLetter Body:\n{result.letter_body[:500]}…")
        if result.tone_note:
            print(f"\nTone Note: {result.tone_note}")
    except Exception as exc:
        print(f"\n❌ FAILED: {type(exc).__name__}: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
