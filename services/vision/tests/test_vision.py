"""Tests for the Vision service.

The tests mock ``_classify_with_gemini`` so they deterministically exercise
the wire contract without requiring Gemini credentials.
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
    spec = importlib.util.spec_from_file_location("vision_main", SERVICE_ROOT / "main.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["vision_main"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def app_module():
    return _load_main()


@pytest.fixture
def client(app_module) -> TestClient:
    return TestClient(app_module.app)


def _mock_classification(category="FIRE", confidence=0.91):
    from aegis_shared.schemas import (
        IncidentCategory,
        VisionClassification,
        VisionEvidence,
    )

    return VisionClassification(
        category=IncidentCategory(category),
        sub_type="KITCHEN_FIRE",
        confidence=confidence,
        evidence=VisionEvidence(flame_visible=True, smoke_density=0.4),
        rationale="Open flame with smoke (mock).",
    )


def test_vision_health(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "vision"


def test_analyze_returns_signal(client: TestClient, app_module) -> None:
    fake_jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 512
    payload = {
        "venue_id": "taj-ahmedabad",
        "camera_id": "K-12",
        "zone_id": "kitchen-main",
        "frame_base64": base64.b64encode(fake_jpeg).decode(),
        "publish": False,
    }
    with patch.object(
        app_module,
        "_classify_with_gemini",
        new=AsyncMock(return_value=(_mock_classification(), "abcd1234")),
    ):
        resp = client.post("/v1/analyze", json=payload)

    assert resp.status_code == 200
    body = resp.json()
    assert body["signal"]["venue_id"] == "taj-ahmedabad"
    assert body["signal"]["modality"] == "VISION"
    assert body["signal"]["category_hint"] == "FIRE"
    assert body["signal"]["confidence"] > 0.5
    assert body["used_gemini"] is True


def test_analyze_rejects_empty(client: TestClient) -> None:
    payload = {
        "venue_id": "V",
        "camera_id": "C",
        "zone_id": "Z",
        "frame_base64": base64.b64encode(b"").decode(),
    }
    resp = client.post("/v1/analyze", json=payload)
    assert resp.status_code == 400


def test_analyze_falls_back_when_gemini_unavailable(client: TestClient, app_module) -> None:
    from aegis_shared.errors import DownstreamServiceError

    fake_jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 512
    payload = {
        "venue_id": "V",
        "camera_id": "C",
        "zone_id": "Z",
        "frame_base64": base64.b64encode(fake_jpeg).decode(),
        "publish": False,
    }
    with patch.object(
        app_module,
        "_classify_with_gemini",
        new=AsyncMock(side_effect=DownstreamServiceError("no key")),
    ):
        resp = client.post("/v1/analyze", json=payload)

    assert resp.status_code == 200
    body = resp.json()
    assert body["used_gemini"] is False
    assert body["signal"]["category_hint"] == "OTHER"


def test_pubsub_raw_frames_acks(client: TestClient, app_module) -> None:
    fake_jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 128
    message = {
        "frame_id": "FRM-test-1",
        "venue_id": "taj-ahmedabad",
        "camera_id": "K-12",
        "zone_id": "kitchen-main",
        "captured_at": "2026-04-24T00:00:00Z",
        "received_at": "2026-04-24T00:00:01Z",
        "content_type": "image/jpeg",
        "bytes_base64": base64.b64encode(fake_jpeg).decode(),
        "size_bytes": len(fake_jpeg),
    }
    envelope = {
        "message": {
            "data": base64.b64encode(json.dumps(message).encode()).decode(),
            "attributes": {"zone_id": "kitchen-main"},
        }
    }
    with (
        patch.object(
            app_module,
            "_classify_with_gemini",
            new=AsyncMock(return_value=(_mock_classification(), "pubsub123")),
        ),
        patch.object(app_module, "publish_json") as mock_publish,
    ):
        mock_publish.return_value.message_id = "msg-1"
        resp = client.post("/pubsub/raw-frames", json=envelope)

    assert resp.status_code == 200
    assert resp.json() == {"ack": "true"}
    mock_publish.assert_called_once()


def test_pubsub_raw_frames_rejects_empty(client: TestClient) -> None:
    resp = client.post("/pubsub/raw-frames", json={"message": {}})
    assert resp.status_code == 400
