"""Ingest service.

Exposes HTTPS endpoints for the edge gateway (or demo clients) to push:
    - camera frames  → POST /v1/frames
    - audio chunks   → POST /v1/audio
    - sensor events  → POST /v1/sensors

Each validated request is:
    1. Stored to Cloud Storage (raw + DLP-redacted variant — redaction in Vision svc)
    2. Published to the corresponding Pub/Sub topic

No heavy processing happens here. This is the thin, high-availability edge.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from aegis_shared import get_settings, setup_logging
from aegis_shared.logger import get_logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import frames, health, sensors


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging("ingest")
    log = get_logger(__name__)
    settings = get_settings()
    log.info(
        "ingest_service_started",
        env=settings.aegis_env,
        project=settings.gcp_project_id,
        region=settings.gcp_region,
    )
    yield
    log.info("ingest_service_stopped")


app = FastAPI(
    title="Aegis Ingest",
    version="0.1.0",
    description="Edge ingest for frames, audio, and sensor events.",
    lifespan=lifespan,
)

# CORS middleware handles preflights and adds headers.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(health.router)
app.include_router(frames.router, prefix="/v1")
app.include_router(sensors.router, prefix="/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)  # noqa: S104
