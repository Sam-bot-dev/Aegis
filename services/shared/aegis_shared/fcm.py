"""Firebase Cloud Messaging helper.

Sends high-priority push notifications via the Firebase Admin SDK. Initialises
once per process using:

    - ``FIREBASE_ADMIN_CREDENTIALS`` (service account JSON) if provided
    - Application Default Credentials otherwise

Fails soft: if initialisation fails (no creds, SDK missing), the send methods
log a warning and return ``None`` so pipeline tests stay green without
Firebase. Real dev + prod use real creds per SETUP.md.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path
from typing import Any

from aegis_shared.config import get_settings
from aegis_shared.logger import get_logger

log = get_logger(__name__)


@lru_cache(maxsize=1)
def _firebase_app() -> Any | None:
    try:
        import firebase_admin  # type: ignore[import-not-found]
        from firebase_admin import credentials  # type: ignore[import-not-found]

        settings = get_settings()
        if firebase_admin._apps:
            return firebase_admin.get_app()

        cred = None
        cred_path = settings.firebase_admin_credentials
        if cred_path and Path(cred_path).is_file():
            cred = credentials.Certificate(cred_path)
        elif (
            settings.google_application_credentials
            and Path(settings.google_application_credentials).is_file()
        ):
            cred = credentials.Certificate(settings.google_application_credentials)

        if cred is not None:
            app = firebase_admin.initialize_app(cred, {"projectId": settings.firebase_project_id})
        else:
            app = firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id})
        log.info("firebase_admin_initialized", project=settings.firebase_project_id)
        return app
    except Exception as exc:
        log.warning("firebase_admin_unavailable", error=str(exc))
        return None


def send_to_tokens(
    tokens: Sequence[str],
    *,
    title: str,
    body: str,
    data: dict[str, str] | None = None,
    high_priority: bool = True,
) -> list[str]:
    """Send a push to the given device tokens.

    Returns a list of tokens that succeeded (empty if Firebase is unavailable).
    """
    app = _firebase_app()
    if app is None or not tokens:
        return []
    try:
        from firebase_admin import messaging  # type: ignore[import-not-found]
    except ImportError:
        return []

    data = data or {}
    data = {k: json.dumps(v) if not isinstance(v, str) else v for k, v in data.items()}

    android = messaging.AndroidConfig(
        priority="high" if high_priority else "normal",
        ttl=300,
        notification=messaging.AndroidNotification(
            sound="default",
            default_vibrate_timings=True,
        ),
    )
    apns = messaging.APNSConfig(
        headers={"apns-priority": "10" if high_priority else "5"},
        payload=messaging.APNSPayload(
            aps=messaging.Aps(
                alert=messaging.ApsAlert(title=title, body=body),
                sound="default",
                content_available=True,
            )
        ),
    )

    successes: list[str] = []
    for token in tokens:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data=data,
            token=token,
            android=android,
            apns=apns,
        )
        try:
            resp = messaging.send(message, app=app)
            successes.append(token)
            log.info("fcm_sent", token=token[:10] + "...", message_id=resp)
        except Exception as exc:
            log.warning("fcm_send_failed", token=token[:10] + "...", error=str(exc))
    return successes


def send_to_topic(
    topic: str,
    *,
    title: str,
    body: str,
    data: dict[str, str] | None = None,
    high_priority: bool = True,
) -> str | None:
    """Send a push to a named FCM topic (e.g. ``venue_abc_staff``)."""
    app = _firebase_app()
    if app is None:
        return None
    try:
        from firebase_admin import messaging  # type: ignore[import-not-found]
    except ImportError:
        return None
    try:
        android = messaging.AndroidConfig(priority="high" if high_priority else "normal")
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            topic=topic,
            android=android,
        )
        return messaging.send(message, app=app)
    except Exception as exc:
        log.warning("fcm_topic_send_failed", topic=topic, error=str(exc))
        return None
