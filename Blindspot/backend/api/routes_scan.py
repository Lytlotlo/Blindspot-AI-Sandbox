from fastapi import APIRouter, Form

from ..core.services.log_service import log_service
from ..core.services.scanner_service import scanner_service

router = APIRouter()


@router.post("/scan/text")
async def scan_text_endpoint(
    input_text: str = Form(...),
    session_id: str = Form("default_session")
):
    """
    Receives a text prompt from a user, sends it to the main scanner service
    for analysis, logs the event, and returns the full analysis result.

    Args:
        input_text: The text prompt to be analyzed.
        session_id: An identifier for the user's session.

    Returns:
        A dictionary containing the detailed security analysis of the prompt.
    """
    result_data = scanner_service.scan_text(input_text, session_id)
    log_service.add_event("text_scan", result_data)
    return result_data