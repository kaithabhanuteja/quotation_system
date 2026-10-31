
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import EmailRecord

from app.services.gemini_service import extract_requirements
from app.services.software_estimator import generate_software_estimate
from app.services.civil_estimator import generate_civil_estimate

from app.services.pdf_generator import generate_software_pdf
from app.services.civil_pdf_generator import generate_civil_pdf


router = APIRouter(
    prefix="/api/estimates",
    tags=["Estimates"]
)


# ---------------- COMMON HELPERS ----------------

def get_email_record(email_id: int, db: Session):
    email_record = db.get(EmailRecord, email_id)

    if email_record is None:
        raise HTTPException(
            status_code=404,
            detail="Email record not found"
        )

    return email_record


def get_email_content(email_record):
    return f"""
    Sender: {email_record.sender or ""}
    Subject: {email_record.subject or ""}

    Email Body:
    {email_record.body or ""}

    Attachment Content:
    {email_record.attachment_text or ""}
    """


def get_customer_details(extracted, email_record):
    return {
        "name": extracted.customer_name,
        "email": extracted.customer_email or email_record.sender,
    }


def detect_industry(email_content):
    extracted = extract_requirements(email_content)
    industry = extracted.industry.lower().strip()

    if industry not in ["software", "civil"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported industry detected: {industry}"
        )

    return extracted, industry


# ---------------- SOFTWARE ESTIMATION ----------------

def create_estimate_from_email(email_id: int, db: Session):
    email_record = get_email_record(email_id, db)
    email_content = get_email_content(email_record)

    extracted, industry = detect_industry(email_content)

    if industry != "software":
        raise HTTPException(
            status_code=400,
            detail=f"This email belongs to {industry}, not software."
        )

    quotation = generate_software_estimate(email_content)
    customer = get_customer_details(extracted, email_record)

    return quotation, customer


@router.post("/software/{email_id}")
def create_software_estimate(
    email_id: int,
    db: Session = Depends(get_db)
):
    try:
        quotation, customer = create_estimate_from_email(
            email_id, db
        )

        return {
            "email_id": email_id,
            "industry": "software",
            "customer": customer,
            "quotation": quotation.model_dump()
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Software estimation failed: {type(error).__name__}"
        )


@router.get("/software/{email_id}/pdf")
def download_software_quotation(
    email_id: int,
    db: Session = Depends(get_db)
):
    try:
        quotation, customer = create_estimate_from_email(
            email_id, db
        )

        pdf_buffer, quote_number = generate_software_pdf(
            quotation, customer
        )

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                    f'attachment; filename="{quote_number}.pdf"'
            }
        )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Software PDF generation failed: {type(error).__name__}"
        )


# ---------------- CIVIL ESTIMATION ----------------

def create_civil_estimate_from_email(email_id: int, db: Session):
    email_record = get_email_record(email_id, db)
    email_content = get_email_content(email_record)

    extracted, industry = detect_industry(email_content)

    if industry != "civil":
        raise HTTPException(
            status_code=400,
            detail=f"This email belongs to {industry}, not civil."
        )

    quotation = generate_civil_estimate(email_content)
    customer = get_customer_details(extracted, email_record)

    return quotation, customer


@router.post("/civil/{email_id}")
def create_civil_estimate_api(
    email_id: int,
    db: Session = Depends(get_db)
):
    try:
        quotation, customer = create_civil_estimate_from_email(
            email_id, db
        )

        return {
            "email_id": email_id,
            "industry": "civil",
            "customer": customer,
            "quotation": quotation.model_dump()
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Civil estimation failed: {type(error).__name__}"
        )


@router.get("/civil/{email_id}/pdf")
def download_civil_quotation(
    email_id: int,
    db: Session = Depends(get_db)
):
    try:
        quotation, customer = create_civil_estimate_from_email(
            email_id, db
        )

        pdf_buffer, quote_number = generate_civil_pdf(
            quotation, customer
        )

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                    f'attachment; filename="{quote_number}.pdf"'
            }
        )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Civil PDF generation failed: {type(error).__name__}"
        )


# ---------------- AUTOMATIC INDUSTRY PDF ----------------

@router.get("/{email_id}/pdf")
def download_quotation_pdf(
    email_id: int,
    db: Session = Depends(get_db)
):
    try:
        email_record = get_email_record(email_id, db)
        email_content = get_email_content(email_record)

        extracted, industry = detect_industry(email_content)
        customer = get_customer_details(extracted, email_record)

        if industry == "software":
            quotation = generate_software_estimate(email_content)

            pdf_buffer, quote_number = generate_software_pdf(
                quotation, customer
            )

        else:
            quotation = generate_civil_estimate(email_content)

            pdf_buffer, quote_number = generate_civil_pdf(
                quotation, customer
            )

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                    f'attachment; filename="{quote_number}.pdf"',
                "X-Quotation-Industry": industry,
                "X-Quotation-Number": quote_number
            }
        )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Quotation generation failed: {type(error).__name__}"
        )
