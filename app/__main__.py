"""
Entry point: `python -m app` starts a Uvicorn server.
The port can be overridden with the PORT environment variable.
"""

import os

import uvicorn


def main() -> None:
    port = int(os.getenv("PORT", "8080"))
    # access_log=False: requests are already logged by our own middleware (plugins/monitoring.py).
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, access_log=False)


if __name__ == "__main__":
    main()
