# Vision service — production container.
# Build from the repo root:
#
#   docker build -f services/vision/Dockerfile -t aegis-vision .

FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Shared lib first for cache reuse.
COPY services/shared /app/shared
RUN pip install /app/shared

# Vision service.
COPY services/vision /app/vision
RUN pip install /app/vision

# Prompts directory shipped so ``load_prompt('vision_classifier')`` succeeds.
COPY prompts /app/prompts

WORKDIR /app/vision

EXPOSE 8002

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8002}"]
