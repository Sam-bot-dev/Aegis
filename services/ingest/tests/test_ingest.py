"""Tests for the ingest service.

Each service's test file uses importlib to load its own `main.py` under a
unique module alias. This prevents sys.modules collisions when the whole
monorepo's tests run in a single pytest session.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parent.parent


def _load_main():
    if str(SERVICE_ROOT) not in sys.path:
        sys.path.insert(0, str(SERVICE_ROOT))
    # Evict any router modules left from a previous service's test run.
    for key in [k for k in sys.modules if k.startswith("routers")]:
        del sys.modules[key]
    spec = importlib.util.spec_from_file_location("ingest_main", SERVICE_ROOT / "main.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["ingest_main"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def app_module():
    return _load_main()


@pytest.fixture
def client(app_module) -> TestClient:
    return TestClient(app_module.app)


def test_health_ok(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "ingest"


def test_ready_ok(client: TestClient) -> None:
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"


def test_frame_ingest_rejects_empty(client: TestClient) -> None:
    with patch("routers.frames.publish_json") as mock_pub:
        resp = client.post(
            "/v1/frames",
            data={"venue_id": "V1", "camera_id": "C1"},
            files={"frame": ("f.jpg", b"", "image/jpeg")},
        )
    assert resp.status_code == 400
    mock_pub.assert_not_called()


def test_frame_ingest_accepts_jpeg(client: TestClient) -> None:
    fake_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 1024
    with patch("routers.frames.publish_json") as mock_pub:
        mock_pub.return_value.message_id = "fake-msg-id"
        resp = client.post(
            "/v1/frames",
            data={
                "venue_id": "taj-ahmedabad",
                "camera_id": "K-12",
                "zone_id": "kitchen-main",
            },
            files={"frame": ("f.jpg", fake_bytes, "image/jpeg")},
        )
    assert resp.status_code == 202
    body = resp.json()
    assert body["venue_id"] == "taj-ahmedabad"
    assert body["camera_id"] == "K-12"
    assert body["message_id"] == "fake-msg-id"
    mock_pub.assert_called_once()
    kwargs = mock_pub.call_args.kwargs
    assert kwargs["payload"]["zone_id"] == "kitchen-main"
    assert kwargs["attributes"]["zone_id"] == "kitchen-main"


def test_sensor_batch_empty_rejected(client: TestClient) -> None:
    resp = client.post("/v1/sensors", json={"venue_id": "V1", "readings": []})
    assert resp.status_code == 400


def test_sensor_batch_accepted(client: TestClient) -> None:
    with patch("routers.sensors.publish_json") as mock_pub:
        mock_pub.return_value.message_id = "msg-xxx"
        payload = {
            "venue_id": "taj-ahmedabad",
            "readings": [
                {
                    "sensor_id": "K-S-07",
                    "sensor_type": "smoke",
                    "zone_id": "kitchen-main",
                    "value": 120.5,
                    "triggered": True,
                },
                {
                    "sensor_id": "K-S-08",
                    "sensor_type": "heat",
                    "zone_id": "kitchen-main",
                    "value": 85.2,
                    "triggered": False,
                },
            ],
        }
        resp = client.post("/v1/sensors", json=payload)
    assert resp.status_code == 202
    body = resp.json()
    assert body["accepted"] == 2
    assert mock_pub.call_count == 2
