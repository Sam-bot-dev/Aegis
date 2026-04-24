"""Sensor event ingest.

POST /v1/sensors — batch of sensor events (smoke, CO, heat, door-state, motion).

Designed to be called from an MQTT → HTTP bridge running in the venue.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from aegis_shared.config import get_settings
from aegis_shared.logger import get_logger
from aegis_shared.pubsub import publish_json
from aegis_shared.schemas import new_id
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

log = get_logger(__name__)
router = APIRouter(tags=["ingest"])


SensorType = Literal["smoke", "co", "heat", "motion", "door", "panic_button"]


class SensorReading(BaseModel):
    sensor_id: str
    sensor_type: SensorType
    zone_id: str
    value: float
    triggered: bool = False
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, object] = Field(default_factory=dict)


class SensorBatch(BaseModel):
    venue_id: str
    readings: list[SensorReading]


class SensorAckResponse(BaseModel):
    accepted: int
    message_ids: list[str]


@router.post(
    "/sensors",
    response_model=SensorAckResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest a batch of sensor readings",
)
async def ingest_sensors(batch: SensorBatch) -> SensorAckResponse:
    """Publish each reading to `sensor-events`.

    Ordering key: `venue_id:sensor_id` so per-sensor event order is preserved.
    """
    if not batch.readings:
        raise HTTPException(status_code=400, detail="empty readings list")
    if len(batch.readings) > 500:
        raise HTTPException(status_code=413, detail="too many readings in one batch")

    settings = get_settings()
    message_ids: list[str] = []

    for reading in batch.readings:
        event_id = new_id("SNS")
        payload = {
            "event_id": event_id,
            "venue_id": batch.venue_id,
            **reading.model_dump(mode="json"),
        }
        result = publish_json(
            topic=settings.pubsub_topic_sensors,
            payload=payload,
            ordering_key=f"{batch.venue_id}:{reading.sensor_id}",
            attributes={
                "venue_id": batch.venue_id,
                "sensor_id": reading.sensor_id,
                "sensor_type": reading.sensor_type,
                "triggered": str(reading.triggered).lower(),
            },
        )
        message_ids.append(result.message_id)

    log.info(
        "sensor_batch_ingested",
        venue_id=batch.venue_id,
        count=len(batch.readings),
    )
    return SensorAckResponse(accepted=len(message_ids), message_ids=message_ids)
