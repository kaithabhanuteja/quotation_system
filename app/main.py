
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine

from app.routers import emails, ai, estimates, pages


# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered Software and Civil Quotation Generator",
    version="1.0.0"
)


# Static files
BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)


# Register API routers
# Prefixes are already defined inside the router files.
app.include_router(emails.router)
app.include_router(ai.router)
app.include_router(estimates.router)
app.include_router(pages.router)


@app.get("/health")
def health_check():
    return {
        "status": "running",
        "application": settings.app_name
    }
