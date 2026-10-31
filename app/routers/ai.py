from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import EmailRecord
from app.schemas import RequirementExtractionRequest
from app.services.gemini_service import (
    extract_requirements,
    test_gemini
)

router = APIRouter(
    prefix="/api/ai",
    tags=["AI"]
)


# Test Gemini API connection
@router.get("/test")
def test_gemini_connection():

    try:
        result = test_gemini()

        return {
            "status": "success",
            "message": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini API error: {type(e).__name__}"
        )


# Extract requirements from uploaded email
@router.post("/extract-requirements")
def extract_email_requirements(
    request: RequirementExtractionRequest,
    db: Session = Depends(get_db)
):

    email_record = db.get(
        EmailRecord,
        request.email_id
    )

    if email_record is None:
        raise HTTPException(
            status_code=404,
            detail="Email record not found"
        )

    content = f"""
    Sender: {email_record.sender or 'Not provided'}

    Subject: {email_record.subject or 'Not provided'}

    Email Body:
    {email_record.body}

    Attachment Content:
    {email_record.attachment_text or 'No attachments'}
    """

    try:
        result = extract_requirements(content)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"AI extraction failed: {type(e).__name__}"
        )