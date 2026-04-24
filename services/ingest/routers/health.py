"""Health + readiness endpoints."""

from __future__ import annotations

from datetime import UTC, datetime

from aegis_shared import get_settings
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    service: str
    env: str
    time: datetime


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness probe. Returns 200 if the process is up."""
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service="ingest",
        env=settings.aegis_env,
        time=datetime.now(UTC),
    )


@router.get("/ready", response_model=HealthResponse)
async def ready() -> HealthResponse:
    """Readiness probe. Could check downstream deps; kept trivial for now."""
    settings = get_settings()
    return HealthResponse(
        status="ready",
        service="ingest",
        env=settings.aegis_env,
        time=datetime.now(UTC),
    )
