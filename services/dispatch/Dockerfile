# Dispatch service — production container.
# Build from the repo root:
#
#   docker build -f services/dispatch/Dockerfile -t aegis-dispatch .

FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY services/shared /app/shared
RUN pip install /app/shared

COPY services/dispatch /app/dispatch
RUN pip install /app/dispatch

# Optional but cheap: ship prompts so any future dispatcher agent prompt is
# loadable in production.
COPY prompts /app/prompts

WORKDIR /app/dispatch

EXPOSE 8004

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8004}"]
