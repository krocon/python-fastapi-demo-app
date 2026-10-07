"""
Validates request bodies right after they are received.

`Title` is a reusable annotated type: every model field declared as `Title`
runs `validate_title`. Errors become 400 responses (see plugins/status_pages.py).
"""

from typing import Annotated

from pydantic import AfterValidator

MAX_TITLE_LENGTH = 100


def validate_title(title: str) -> str:
    if not title.strip():
        raise ValueError("title must not be blank")
    if len(title) > MAX_TITLE_LENGTH:
        raise ValueError(f"title must be at most {MAX_TITLE_LENGTH} characters")
    return title


Title = Annotated[str, AfterValidator(validate_title)]
