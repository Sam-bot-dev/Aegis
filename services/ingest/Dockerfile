# Ingest service — production container.
# Built by Cloud Build, deployed to Cloud Run.

FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Shared library first (separate layer → better caching).
COPY services/shared /app/shared
RUN pip install /app/shared

# Ingest service.
COPY services/ingest /app/ingest
RUN pip install /app/ingest

WORKDIR /app/ingest

EXPOSE 8001

# Cloud Run sets $PORT; default 8001 for local docker runs.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001}"]
