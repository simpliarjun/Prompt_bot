"""
PDF generation service using fpdf2.

Correction #9: DejaVu Sans fonts vendored and referenced by module-relative path.
§13 layout: sender block, date, recipient, subject, salutation, body, closing, footer.
§16: strip control characters before rendering.
"""

import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from fpdf import FPDF

from logging_config import get_logger

logger = get_logger(__name__)

# Font directory resolved relative to this module, never CWD-relative.
_FONTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"
_DEJAVU_REGULAR = str(_FONTS_DIR / "DejaVuSans.ttf")
_DEJAVU_BOLD = str(_FONTS_DIR / "DejaVuSans-Bold.ttf")


def _strip_control_chars(text: str) -> str:
    """Remove control characters that could corrupt the PDF, keeping newlines/tabs."""
    return "".join(
        ch for ch in text
        if ch in ("\n", "\r", "\t") or not unicodedata.category(ch).startswith("C")
    )


def _slugify(text: str) -> str:
    """Simple slugification for filenames."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "_", text)
    return text[:60]


def generate_pdf(grievance: dict) -> bytes:
    """
    Generate a PDF from a grievance document dict.

    Returns raw PDF bytes.
    """
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=25)

    # Embed Unicode fonts (correction #9)
    pdf.add_font("DejaVu", "", _DEJAVU_REGULAR)
    pdf.add_font("DejaVu", "B", _DEJAVU_BOLD)

    pdf.add_page()
    page_width = pdf.w - pdf.l_margin - pdf.r_margin

    # --- 1. Sender block (top-left) ---
    pdf.set_font("DejaVu", "", 10)
    contact_name = _strip_control_chars(grievance.get("contact_name", ""))
    contact_email = _strip_control_chars(grievance.get("contact_email", ""))
    contact_phone = grievance.get("contact_phone")

    pdf.cell(0, 5, contact_name, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, contact_email, new_x="LMARGIN", new_y="NEXT")
    if contact_phone:
        pdf.cell(0, 5, _strip_control_chars(contact_phone), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # --- 2. Date (right-aligned) ---
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%B %d, %Y")
    pdf.cell(0, 5, date_str, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # --- 3. Recipient block ---
    company_name = _strip_control_chars(grievance.get("company_name", ""))
    pdf.cell(0, 5, company_name, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "Customer Relations Department", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # --- 4. Subject line (bold) ---
    subject_line = _strip_control_chars(grievance.get("subject_line", ""))
    pdf.set_font("DejaVu", "B", 11)
    pdf.multi_cell(page_width, 6, f"RE: {subject_line}")
    pdf.ln(5)

    # --- 5. Salutation ---
    pdf.set_font("DejaVu", "", 10)
    pdf.cell(0, 5, f"Dear {company_name} Customer Relations Team,", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # --- 6. Body (justified) ---
    letter_body = _strip_control_chars(grievance.get("letter_body", ""))
    # Split paragraphs and render each
    paragraphs = letter_body.split("\n\n") if "\n\n" in letter_body else [letter_body]
    for para in paragraphs:
        para = para.strip()
        if para:
            pdf.multi_cell(page_width, 5, para, align="J")
            pdf.ln(3)

    pdf.ln(5)

    # --- 7. Closing ---
    pdf.cell(0, 5, "Sincerely,", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.cell(0, 5, contact_name, new_x="LMARGIN", new_y="NEXT")

    # --- 8. Footer ---
    pdf.ln(15)
    pdf.set_font("DejaVu", "", 7)
    pdf.set_text_color(128, 128, 128)

    disclaimer = (
        "Drafted with AI assistance based on information provided by the sender. "
        "This letter does not constitute legal advice."
    )
    grievance_id = grievance.get("id", grievance.get("_id", "N/A"))
    export_time = now.strftime("%Y-%m-%d %H:%M UTC")
    footer_text = f"{disclaimer}\nReference: {grievance_id} | Exported: {export_time}"
    pdf.multi_cell(page_width, 4, footer_text, align="C")

    return pdf.output()


def get_pdf_filename(grievance: dict) -> str:
    """Build the download filename per §13 convention."""
    company_slug = _slugify(grievance.get("company_name", "unknown"))
    incident_date = grievance.get("incident_date", "undated")
    if hasattr(incident_date, "isoformat"):
        incident_date = incident_date.isoformat()
    return f"grievance_{company_slug}_{incident_date}.pdf"
