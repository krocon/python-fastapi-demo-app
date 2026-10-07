"""Maps exceptions to clean JSON error responses with the right HTTP status."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from starlette.exceptions import HTTPException

from app.plugins.serialization import PrettyJSONResponse

logger = logging.getLogger("app.errors")


class ErrorResponse(BaseModel):
    message: str


def _error(status_code: int, message: str) -> PrettyJSONResponse:
    return PrettyJSONResponse(ErrorResponse(message=message).model_dump(), status_code=status_code)


def _describe(error: dict) -> str:
    # Our own validators raise ValueError("title must not be blank") – show that text as is.
    if error["type"] == "value_error":
        return str(error["ctx"]["error"])
    field = ".".join(str(part) for part in error["loc"][1:]) or "body"
    return f"{field}: {error['msg']}"


def configure_status_pages(app: FastAPI) -> None:

    # FastAPI answers invalid input with 422 by default; we use 400 like the Ktor app.
    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        return _error(status.HTTP_400_BAD_REQUEST, ", ".join(_describe(e) for e in exc.errors()))

    # Raised by routes, e.g. HTTPException(404, "Task 42 not found").
    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        return _error(exc.status_code, str(exc.detail))

    @app.exception_handler(Exception)
    async def unhandled_error(request: Request, exc: Exception):
        logger.error("Unhandled error", exc_info=exc)
        return _error(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error")
