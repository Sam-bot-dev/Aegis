# Orchestrator service — production container.
# Build context must be the repo root so we can COPY services/shared,
# agents/, and prompts/. Example:
#
#   docker build -f services/orchestrator/Dockerfile -t aegis-orchestrator .

FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 1. Shared lib (separate layer for caching).
COPY services/shared /app/shared
RUN pip install /app/shared

# 2. Agent suite (depends on aegis-shared).
COPY agents /app/agents
RUN pip install /app/agents

# 3. Orchestrator service. We install --no-deps because pip cannot resolve the
# uv path-based sources for aegis-shared / aegis-agents — they're already
# installed above. The explicit deps list mirrors orchestrator/pyproject.toml.
COPY services/orchestrator /app/orchestrator
RUN pip install --no-deps /app/orchestrator \
 && pip install "fastapi>=0.115.0" "uvicorn[standard]>=0.30.0" \
                 "google-cloud-aiplatform>=1.70.0" "google-genai>=0.3.0"

# 4. Prompts directory so PromptRegistry resolves ``load_prompt('...')``.
COPY prompts /app/prompts

WORKDIR /app/orchestrator

EXPOSE 8003

# Cloud Run sets $PORT; default 8003 for local docker runs.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8003}"]
