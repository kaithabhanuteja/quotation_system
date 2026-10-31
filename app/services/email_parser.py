from email import policy
from email.parser import BytesParser
from io import BytesIO

import fitz


def extract_pdf_text(data: bytes) -> str:
    text_parts = []
    with fitz.open(stream=data, filetype="pdf") as document:
        for page in document:
            page_text = page.get_text("text").strip()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts)


def _decode_part(part) -> str:
    payload = part.get_payload(decode=True)
    if not payload:
        return ""
    charset = part.get_content_charset() or "utf-8"
    try:
        return payload.decode(charset, errors="replace")
    except LookupError:
        return payload.decode("utf-8", errors="replace")


def parse_eml(data: bytes) -> dict:
    message = BytesParser(policy=policy.default).parsebytes(data)
    body_parts = []
    attachment_text_parts = []

    if message.is_multipart():
        for part in message.walk():
            if part.is_multipart():
                continue

            content_type = part.get_content_type()
            filename = part.get_filename()

            if content_type == "text/plain" and not filename:
                content = part.get_content()
                if isinstance(content, str) and content.strip():
                    body_parts.append(content.strip())

            elif filename and content_type == "application/pdf":
                payload = part.get_payload(decode=True)
                if payload:
                    try:
                        extracted = extract_pdf_text(payload)
                        if extracted:
                            attachment_text_parts.append(
                                f"[Attachment: {filename}]\n{extracted}"
                            )
                    except Exception as exc:
                        attachment_text_parts.append(
                            f"[Attachment: {filename} - PDF text extraction failed: {exc}]"
                        )
    else:
        content = message.get_content()
        if isinstance(content, str):
            body_parts.append(content.strip())

    return {
        "sender": message.get("From"),
        "subject": message.get("Subject"),
        "body": "\n\n".join(body_parts).strip(),
        "attachment_text": "\n\n".join(attachment_text_parts).strip() or None,
    }


def parse_uploaded_file(filename: str, data: bytes) -> dict:
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if suffix == "eml":
        return parse_eml(data)

    if suffix == "txt":
        return {
            "sender": None,
            "subject": None,
            "body": data.decode("utf-8-sig", errors="replace").strip(),
            "attachment_text": None,
        }

    if suffix == "pdf":
        return {
            "sender": None,
            "subject": filename,
            "body": "Text extracted from uploaded PDF document.",
            "attachment_text": extract_pdf_text(data),
        }

    raise ValueError("Unsupported file type. Upload .eml, .txt, or .pdf.")
