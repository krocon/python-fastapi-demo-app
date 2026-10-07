FROM python:3.13-slim

# uv installs the locked dependencies (fast, reproducible).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY app ./app

ENV PATH="/app/.venv/bin:$PATH" \
    PORT=8080
EXPOSE 8080
CMD ["python", "-m", "app"]
