
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parents[1]

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

router = APIRouter(tags=["Frontend"])


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "page_title": "Dashboard"
        }
    )
