"""Frame ingest endpoints.

POST /v1/frames — multipart upload of a single JPEG frame from a camera.

For Phase 1 we keep this dead-simple: accept bytes, stamp metadata, publish
a Pub/Sub message with a reference (or inline for small frames). The Vision
service consumes the message and runs Gemini.

In Phase 2 we'll add:
    - mTLS auth for edge gateway
    - Cloud Storage write with DLP pre-redaction
    - App Check token validation
"""

from __future__ import annotations

import base64
from datetime import UTC, datetime
from typing import Annotated

from aegis_shared.config import get_settings
from aegis_shared.logger import get_logger
from aegis_shared.pubsub import publish_json
from aegis_shared.schemas import new_id
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

log = get_logger(__name__)
router = APIRouter(tags=["ingest"])

MAX_FRAME_BYTES = 5 * 1024 * 1024  # 5 MB per frame


class FrameAckResponse(BaseModel):
    frame_id: str
    message_id: str
    venue_id: str
    camera_id: str
    received_at: datetime


@router.post(
    "/frames",
    response_model=FrameAckResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest a single camera frame",
)
async def ingest_frame(
    venue_id: Annotated[str, Form(description="Venue identifier")],
    camera_id: Annotated[str, Form(description="Camera identifier within the venue")],
    frame: Annotated[UploadFile, File(description="JPEG frame bytes")],
    zone_id: Annotated[str | None, Form(description="Optional mapped zone identifier")] = None,
    captured_at: Annotated[datetime | None, Form()] = None,
) -> FrameAckResponse:
    """Accept a single JPEG frame and publish it to `raw-frames`.

    Phase 1: inline base64 payload for simplicity (demo-friendly).
    Phase 2: write to GCS, publish only the URI + metadata.
    """
    settings = get_settings()

    raw = await frame.read()
    if len(raw) == 0:
        raise HTTPException(status_code=400, detail="empty frame body")
    if len(raw) > MAX_FRAME_BYTES:
        raise HTTPException(status_code=413, detail="frame exceeds 5 MB limit")
    if frame.content_type not in {"image/jpeg", "image/jpg", "image/png"}:
        log.warning("frame_unexpected_content_type", content_type=frame.content_type)

    frame_id = new_id("FRM")
    received_at = datetime.now(UTC)
    captured_ts = (captured_at or received_at).isoformat()

    payload: dict[str, object] = {
        "frame_id": frame_id,
        "venue_id": venue_id,
        "camera_id": camera_id,
        "zone_id": zone_id,
        "captured_at": captured_ts,
        "received_at": received_at.isoformat(),
        "content_type": frame.content_type or "image/jpeg",
        "bytes_base64": base64.b64encode(raw).decode("ascii"),
        "size_bytes": len(raw),
    }

    result = publish_json(
        topic=settings.pubsub_topic_raw_frames,
        payload=payload,
        ordering_key=f"{venue_id}:{camera_id}",
        attributes={
            "venue_id": venue_id,
            "camera_id": camera_id,
            "kind": "frame",
            "zone_id": zone_id or "",
        },
    )

    log.info(
        "frame_ingested",
        frame_id=frame_id,
        venue_id=venue_id,
        camera_id=camera_id,
        size_bytes=len(raw),
        message_id=result.message_id,
    )

    return FrameAckResponse(
        frame_id=frame_id,
        message_id=result.message_id,
        venue_id=venue_id,
        camera_id=camera_id,
        received_at=received_at,
    )
