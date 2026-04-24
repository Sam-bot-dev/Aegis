"""Tests for the orchestrator service.

These tests mock the ``ClassifierAgent`` / ``CascadeAgent`` so the behaviour is
deterministic in CI without Gemini credentials. The real agents are exercised
by the eval harness (Phase 2).
"""

from __future__ import annotations

import base64
import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parent.parent


def _load_main():
    if str(SERVICE_ROOT) not in sys.path:
        sys.path.insert(0, str(SERVICE_ROOT))
    for key in [k for k in sys.modules if k.startswith("routers")]:
        del sys.modules[key]
    spec = importlib.util.spec_from_file_location("orchestrator_main", SERVICE_ROOT / "main.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["orchestrator_main"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def app_module():
    return _load_main()


@pytest.fixture
def client(app_module) -> TestClient:
    return TestClient(app_module.app)


def _signal(category: str = "FIRE", confidence: float = 0.9) -> dict:
    return {
        "venue_id": "taj-ahmedabad",
        "zone_id": "kitchen-main",
        "modality": "VISION",
        "category_hint": category,
        "confidence": confidence,
    }


def _classification(severity: str, category: str = "FIRE", confidence: float = 0.9):
    from aegis_shared.schemas import IncidentClassification

    return IncidentClassification(
        category=category,
        sub_type="KITCHEN_FIRE",
        severity=severity,
        confidence=confidence,
        rationale=f"Mock {severity}/{category}",
    )


def test_health(client: TestClient) -> None:
    assert client.get("/health").json()["service"] == "orchestrator"


def test_high_confidence_fire_triggers_dispatch(client: TestClient, app_module) -> None:
    from agents.classifier.agent import ClassifierAgent

    with (
        patch.object(ClassifierAgent, "run", new=AsyncMock(return_value=_classification("S2"))),
        patch.object(app_module, "publish_json") as mock_pub,
        patch.object(app_module, "upsert_incident", new=AsyncMock()),
        patch.object(app_module, "upsert_dispatch", new=AsyncMock()),
        patch.object(app_module, "append_incident_event", new=AsyncMock()),
        patch.object(app_module, "get_responders_for_venue", new=AsyncMock(return_value=[])),
    ):
        mock_pub.return_value.message_id = "msg"
        resp = client.post("/v1/handle", json=_signal("FIRE", 0.9))

    assert resp.status_code == 200
    body = resp.json()
    assert body["result"]["classification"]["severity"] == "S2"
    assert body["dispatched"] is True
    # At minimum: 1 incident event + 1 dispatch event per paged responder.
    assert mock_pub.call_count >= 2


def test_low_confidence_monitors_without_dispatch(client: TestClient, app_module) -> None:
    from agents.classifier.agent import ClassifierAgent

    with (
        patch.object(ClassifierAgent, "run", new=AsyncMock(return_value=_classification("S3"))),
        patch.object(app_module, "publish_json") as mock_pub,
        patch.object(app_module, "upsert_incident", new=AsyncMock()),
        patch.object(app_module, "upsert_dispatch", new=AsyncMock()),
        patch.object(app_module, "append_incident_event", new=AsyncMock()),
        patch.object(app_module, "get_responders_for_venue", new=AsyncMock(return_value=[])),
    ):
        mock_pub.return_value.message_id = "msg"
        resp = client.post("/v1/handle", json=_signal("FIRE", 0.6))

    assert resp.status_code == 200
    body = resp.json()
    assert body["result"]["classification"]["severity"] == "S3"
    assert body["dispatched"] is False
    # Incident event only (S3 does not dispatch).
    assert mock_pub.call_count == 1


def test_noise_dismissed(client: TestClient, app_module) -> None:
    from agents.classifier.agent import ClassifierAgent

    with (
        patch.object(
            ClassifierAgent,
            "run",
            new=AsyncMock(return_value=_classification("S4", category="OTHER", confidence=0.1)),
        ),
        patch.object(app_module, "publish_json") as mock_pub,
        patch.object(app_module, "upsert_incident", new=AsyncMock()),
        patch.object(app_module, "upsert_dispatch", new=AsyncMock()),
        patch.object(app_module, "append_incident_event", new=AsyncMock()),
        patch.object(app_module, "get_responders_for_venue", new=AsyncMock(return_value=[])),
    ):
        mock_pub.return_value.message_id = "msg"
        resp = client.post("/v1/handle", json=_signal("OTHER", 0.1))

    assert resp.status_code == 200
    body = resp.json()
    assert body["result"]["classification"]["severity"] == "S4"
    assert body["dispatched"] is False


def test_pubsub_perceptual_signals_acknowledges(client: TestClient, app_module) -> None:
    envelope = {
        "message": {
            "data": base64.b64encode(json.dumps(_signal("FIRE", 0.92)).encode()).decode(),
        }
    }
    with patch.object(app_module, "handle_batch", new=AsyncMock(return_value=None)) as mock_handle:
        resp = client.post("/pubsub/perceptual-signals", json=envelope)

    assert resp.status_code == 200
    assert resp.json() == {"ack": "true"}
    mock_handle.assert_awaited_once()
