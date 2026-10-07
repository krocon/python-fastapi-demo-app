"""Registers all HTTP routes of the application."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.live.live_routes import router as live_router
from app.tasks.task_routes import router as task_router

STATIC_DIR = Path(__file__).parent.parent / "static"


def configure_routing(app: FastAPI) -> None:

    @app.get("/", response_class=HTMLResponse)
    async def hello() -> str:
        return '<h1>Hello, FastAPI!</h1>\n<p><a href="/live/">Open the live demo &rarr;</a></p>'

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "UP"}

    # Order matters: /tasks/events must be registered before /tasks/{task_id}.
    app.include_router(live_router)
    app.include_router(task_router)

    # Browser demo page for the live endpoints: http://localhost:8080/live/
    app.mount("/live", StaticFiles(directory=STATIC_DIR, html=True), name="live")
