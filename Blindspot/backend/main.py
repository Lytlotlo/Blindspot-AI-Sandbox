"""
Main application file for the Blindspot AI Security Sandbox.

This file initializes the FastAPI application, mounts the static frontend files,
and includes all the necessary API routers.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api import routes_dashboard, routes_scan

# Initialize the main FastAPI application instance
app = FastAPI(title="Blindspot AI Security Sandbox")

# Define the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Mount the 'static' directory to serve frontend assets like CSS and JavaScript
app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend" / "static"), name="static")

# Include the API routers from other modules to organize the endpoints
app.include_router(routes_dashboard.router, tags=["Dashboard"])
app.include_router(routes_scan.router, prefix="/api", tags=["Scanner"])


@app.get("/health")
def health_check():
    """A simple health check endpoint to confirm the server is running."""
    return {"status": "ok"}