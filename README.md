# AI-Powered Multi-Industry Quotation Generator

Initial backend foundation:
- FastAPI application
- MySQL connection through SQLAlchemy
- Email/file ingestion for `.eml`, `.txt`, and `.pdf`
- Text extraction from email bodies and PDF attachments
- Uploaded email records stored in MySQL

## 1. Create the database

Run this in MySQL:

```sql
CREATE DATABASE quotation_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 2. Configure environment

Copy `.env.example` to `.env` and update `DATABASE_URL`.

Example:
`mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/quotation_db`

## 3. Install and run (Windows PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## 4. Test email upload

Use `POST /api/emails/upload` in Swagger and upload:
- `.eml` email file
- `.txt` email text
- `.pdf` email/requirement document

The endpoint returns the extracted subject, sender, body, attachment text, and database ID.

## Next modules

1. Gmail integration
2. Gemini industry classification and structured extraction
3. Software, civil, and medical estimation engines
4. Industry-specific quotation PDF templates
5. Dashboard and downloadable quotation history
