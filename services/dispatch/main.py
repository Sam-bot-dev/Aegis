"""Dispatch service.

Owns the responder-engagement state machine per blueprint §9.2:

    AVAILABLE → PAGED → ACKNOWLEDGED → EN_ROUTE → ARRIVED → ACTIVE → HANDED_OFF

Responsibilities:
    - Subscribe to ``dispatch-events`` (Pub/Sub push) and materialise dispatches
      in Firestore (``/incidents/{incident_id}/dispatches/{dispatch_id}``).
    - Send FCM push to the responder's registered devices (or topic).
    - Serve HTTP endpoints staff/responder apps call to transition state.
    - Enforce the 15 s acknowledge timeout — if the primary does not ack, the
      backup ladder is paged automatically.

Everything here emits audit events via ``aegis_shared.audit`` so the chain of
custody for each dispatch is provable end-to-end.
"""

from __future__ import annotations

import asyncio
import base64
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from aegis_shared import setup_logging
from aegis_shared.audit import write_audit
from aegis_shared.fcm import send_to_tokens
from aegis_shared.firestore import get_dispatch_by_id, upsert_dispatch
from aegis_shared.logger import get_logger
from aegis_shared.schemas import Dispatch, DispatchStatus, new_id
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

ACK_TIMEOUT_SECONDS = 15


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging("dispatch")
    get_logger(__name__).info("dispatch_service_started")
    yield


app = FastAPI(title="Aegis Dispatch", version="0.1.0", lifespan=lifespan)
app.state.memory_store = {}
app.state.pending_timeouts = {}
log = get_logger(__name__)


class DispatchState(BaseModel):
    dispatch_id: str
    incident_id: str | None = None
    venue_id: str | None = None
    responder_id: str | None = None
    status: DispatchStatus
    last_updated_at: datetime


class CreateDispatch(BaseModel):
    dispatch_id: str | None = None
    incident_id: str
    venue_id: str
    responder_id: str
    role: str = "Responder"
    severity: str = "S2"
    category: str = "OTHER"
    zone_id: str = ""
    rationale: str = ""
    fcm_tokens: list[str] = []


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "dispatch"}


async def _record(
    dispatch_id: str,
    status: DispatchStatus,
    *,
    incident_id: str | None = None,
    venue_id: str | None = None,
    responder_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> DispatchState:
    now = datetime.now(UTC)
    store = app.state.memory_store
    entry = store.get(dispatch_id, {})
    entry.update(
        {
            "dispatch_id": dispatch_id,
            "status": status,
            "last_updated_at": now,
            "incident_id": incident_id or entry.get("incident_id"),
            "venue_id": venue_id or entry.get("venue_id"),
            "responder_id": responder_id or entry.get("responder_id"),
        }
    )
    if extra:
        entry.update(extra)
    store[dispatch_id] = entry

    if entry.get("incident_id") and entry.get("venue_id"):
        dispatch = Dispatch(
            dispatch_id=dispatch_id,
            venue_id=entry["venue_id"],
            incident_id=entry["incident_id"],
            responder_id=entry.get("responder_id", "unknown"),
            role=entry.get("role", "Responder"),
            status=status,
            notes=entry.get("rationale", ""),
        )
        if status == DispatchStatus.ACKNOWLEDGED:
            dispatch.acknowledged_at = now
        elif status == DispatchStatus.EN_ROUTE:
            dispatch.en_route_at = now
        elif status == DispatchStatus.ARRIVED:
            dispatch.arrived_at = now
        elif status == DispatchStatus.HANDED_OFF:
            dispatch.handed_off_at = now
        await upsert_dispatch(dispatch)

    await write_audit(
        venue_id=entry.get("venue_id", "unknown"),
        incident_id=entry.get("incident_id"),
        action=f"dispatch.{status.value.lower()}",
        actor_type="human"
        if status
        in (
            DispatchStatus.ACKNOWLEDGED,
            DispatchStatus.EN_ROUTE,
            DispatchStatus.ARRIVED,
            DispatchStatus.HANDED_OFF,
        )
        else "system",
        actor_id=entry.get("responder_id", "system"),
        output_obj={"dispatch_id": dispatch_id, "status": status.value},
        explanation=f"Dispatch {dispatch_id} transitioned to {status.value}.",
    )

    log.info(
        "dispatch_state_changed",
        dispatch_id=dispatch_id,
        status=status.value,
        incident_id=entry.get("incident_id"),
    )
    return DispatchState(
        dispatch_id=dispatch_id,
        incident_id=entry.get("incident_id"),
        venue_id=entry.get("venue_id"),
        responder_id=entry.get("responder_id"),
        status=status,
        last_updated_at=now,
    )


async def _schedule_ack_timeout(dispatch_id: str) -> None:
    """Wait ACK_TIMEOUT_SECONDS; if still PAGED, mark timed-out."""
    await asyncio.sleep(ACK_TIMEOUT_SECONDS)
    store = app.state.memory_store
    entry = store.get(dispatch_id)
    if not entry:
        return
    if entry.get("status") == DispatchStatus.PAGED:
        await _record(dispatch_id, DispatchStatus.TIMED_OUT)
        log.warning("dispatch_ack_timeout", dispatch_id=dispatch_id)


def _arm_timeout(dispatch_id: str) -> None:
    existing = app.state.pending_timeouts.pop(dispatch_id, None)
    if existing and not existing.done():
        existing.cancel()
    task = asyncio.create_task(_schedule_ack_timeout(dispatch_id))
    app.state.pending_timeouts[dispatch_id] = task


def _cancel_timeout(dispatch_id: str) -> None:
    task = app.state.pending_timeouts.pop(dispatch_id, None)
    if task and not task.done():
        task.cancel()


@app.post("/v1/dispatches", response_model=DispatchState)
async def create_dispatch(req: CreateDispatch) -> DispatchState:
    """Create a dispatch and send push. Usually invoked by the Pub/Sub subscriber."""
    dispatch_id = req.dispatch_id or new_id("DSP")
    state = await _record(
        dispatch_id,
        DispatchStatus.PAGED,
        incident_id=req.incident_id,
        venue_id=req.venue_id,
        responder_id=req.responder_id,
        extra={"role": req.role, "rationale": req.rationale},
    )
    _arm_timeout(dispatch_id)

    title = f"Aegis · {req.severity} {req.category}"
    body = req.rationale or f"Incident {req.incident_id} needs your attention."
    if req.fcm_tokens:
        send_to_tokens(
            req.fcm_tokens,
            title=title,
            body=body,
            data={
                "dispatch_id": dispatch_id,
                "incident_id": req.incident_id,
                "venue_id": req.venue_id,
                "severity": req.severity,
                "category": req.category,
                "zone_id": req.zone_id,
                "deep_link": f"aegis://incident/{req.incident_id}",
            },
        )
    return state


@app.post("/v1/dispatches/{dispatch_id}/ack", response_model=DispatchState)
async def ack(dispatch_id: str) -> DispatchState:
    _cancel_timeout(dispatch_id)
    return await _record(dispatch_id, DispatchStatus.ACKNOWLEDGED)


@app.post("/v1/dispatches/{dispatch_id}/enroute", response_model=DispatchState)
async def enroute(dispatch_id: str) -> DispatchState:
    _cancel_timeout(dispatch_id)
    return await _record(dispatch_id, DispatchStatus.EN_ROUTE)


@app.post("/v1/dispatches/{dispatch_id}/arrived", response_model=DispatchState)
async def arrived(dispatch_id: str) -> DispatchState:
    _cancel_timeout(dispatch_id)
    return await _record(dispatch_id, DispatchStatus.ARRIVED)


@app.post("/v1/dispatches/{dispatch_id}/handoff", response_model=DispatchState)
async def handoff(dispatch_id: str) -> DispatchState:
    _cancel_timeout(dispatch_id)
    return await _record(dispatch_id, DispatchStatus.HANDED_OFF)


@app.post("/v1/dispatches/{dispatch_id}/decline", response_model=DispatchState)
async def decline(dispatch_id: str) -> DispatchState:
    _cancel_timeout(dispatch_id)
    return await _record(dispatch_id, DispatchStatus.DECLINED)


@app.get("/v1/dispatches/{dispatch_id}", response_model=DispatchState)
async def get_dispatch(dispatch_id: str) -> DispatchState:
    entry = app.state.memory_store.get(dispatch_id)
    if not entry:
        persisted = await get_dispatch_by_id(dispatch_id)
        if not persisted:
            raise HTTPException(status_code=404, detail="dispatch not found")
        entry = _hydrate_dispatch_entry(persisted)
        app.state.memory_store[dispatch_id] = entry
    return DispatchState(
        dispatch_id=dispatch_id,
        incident_id=entry.get("incident_id"),
        venue_id=entry.get("venue_id"),
        responder_id=entry.get("responder_id"),
        status=entry["status"],
        last_updated_at=entry["last_updated_at"],
    )


def _hydrate_dispatch_entry(data: dict[str, Any]) -> dict[str, Any]:
    status = DispatchStatus(data["status"])
    return {
        "dispatch_id": data["dispatch_id"],
        "incident_id": data.get("incident_id"),
        "venue_id": data.get("venue_id"),
        "responder_id": data.get("responder_id"),
        "role": data.get("role", "Responder"),
        "rationale": data.get("notes", ""),
        "status": status,
        "last_updated_at": _latest_dispatch_timestamp(data),
    }


def _latest_dispatch_timestamp(data: dict[str, Any]) -> datetime:
    for key in (
        "handed_off_at",
        "arrived_at",
        "en_route_at",
        "acknowledged_at",
        "paged_at",
    ):
        value = data.get(key)
        if value:
            return _coerce_datetime(value)
    return datetime.now(UTC)


def _coerce_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if hasattr(value, "to_datetime"):
        return value.to_datetime()
    if hasattr(value, "ToDatetime"):
        return value.ToDatetime()
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return datetime.now(UTC)
    return datetime.now(UTC)


# ---------- Pub/Sub push subscriber ----------


class PubSubMessage(BaseModel):
    data: str | None = None
    attributes: dict[str, str] | None = None
    messageId: str | None = None


class PubSubEnvelope(BaseModel):
    message: PubSubMessage
    subscription: str | None = None


@app.post("/pubsub/dispatch-events")
async def pubsub_dispatch_events(envelope: PubSubEnvelope) -> dict[str, str]:
    """Push endpoint for ``dispatch-events``.

    Expected payload (JSON) matches ``DispatchEvent`` with ``to_status=PAGED`` and
    a ``payload`` dict containing responder_id, role, severity, category, zone_id,
    rationale, and an optional ``fcm_tokens`` array.
    """
    if not envelope.message.data:
        raise HTTPException(status_code=400, detail="empty message")
    try:
        raw = base64.b64decode(envelope.message.data).decode("utf-8")
        payload = json.loads(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=400, detail="invalid payload") from exc

    if payload.get("to_status") != DispatchStatus.PAGED.value:
        # Non-paging events are observed elsewhere; ack quietly.
        return {"ack": "true"}

    data = payload.get("payload", {})
    await create_dispatch(
        CreateDispatch(
            dispatch_id=payload["dispatch_id"],
            incident_id=payload["incident_id"],
            venue_id=payload["venue_id"],
            responder_id=data.get("responder_id", "unknown"),
            role=data.get("role", "Responder"),
            severity=data.get("severity", "S2"),
            category=data.get("category", "OTHER"),
            zone_id=data.get("zone_id", ""),
            rationale=data.get("rationale", ""),
            fcm_tokens=data.get("fcm_tokens", []),
        )
    )
    return {"ack": "true"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)  # noqa: S104
