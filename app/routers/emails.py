from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import EmailRecord
from app.schemas import EmailUploadResponse
from app.services.email_parser import parse_uploaded_file


router = APIRouter(prefix="/api/emails", tags=["Emails"])


@router.post("/upload", response_model=EmailUploadResponse)
async def upload_email(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    filename = file.filename or "uploaded_file"
    allowed_extensions = {".eml", ".txt", ".pdf"}

    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file. Upload an .eml, .txt, or .pdf file.",
        )

    content = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024

    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {settings.max_upload_mb} MB limit.",
        )

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        parsed = parse_uploaded_file(filename, content)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse file: {exc}")

    if not parsed.get("body") and not parsed.get("attachment_text"):
        raise HTTPException(
            status_code=422,
            detail="No readable text was found in the uploaded file.",
        )

    record = EmailRecord(
        source="upload",
        original_filename=filename,
        sender=parsed.get("sender"),
        subject=parsed.get("subject"),
        body=parsed.get("body") or "",
        attachment_text=parsed.get("attachment_text"),
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@router.get("/list")
def list_emails(db: Session = Depends(get_db)):
    emails = (
        db.query(EmailRecord)
        .order_by(EmailRecord.created_at.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "id": email.id,
            "sender": email.sender,
            "subject": email.subject,
            "body": (email.body or "")[:300],
            "source": email.source,
            "created_at": (
                email.created_at.isoformat()
                if email.created_at else None
            )
        }
        for email in emails
    ]