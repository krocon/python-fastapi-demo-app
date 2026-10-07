"""Logs every incoming request (method, path, status, duration)."""

import logging
import time

from fastapi import FastAPI, Request

logger = logging.getLogger("app.requests")


def configure_monitoring(app: FastAPI) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-5s %(name)s - %(message)s")

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info("%s %s -> %s (%.1f ms)", request.method, request.url.path, response.status_code, duration_ms)
        return response
