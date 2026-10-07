"""
Converts responses to JSON.

FastAPI serializes Pydantic models out of the box; this class only switches
the output to pretty-printed JSON so it is easy to read in curl and videos.
"""

import json
from typing import Any

from fastapi.responses import JSONResponse


class PrettyJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(content, indent=2, ensure_ascii=False).encode("utf-8")
