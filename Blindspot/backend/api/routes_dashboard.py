from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from ..core.services.log_service import log_service

router = APIRouter()

# Define project directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    """Serves the main HTML page for the application."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/api/events")
async def get_events_data():
    """Provides the latest scan events as JSON for the frontend to fetch."""
    events = log_service.get_events()
    return JSONResponse(content=events)