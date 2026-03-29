FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

COPY --from=ghcr.io/astral-sh/uv:0.6.9 /uv /uvx /bin/

WORKDIR /service

COPY pyproject.toml ./
RUN uv sync --no-dev

COPY app ./app
COPY docs ./docs
COPY README.md .
COPY .env.example .

EXPOSE 37612

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "37612"]
