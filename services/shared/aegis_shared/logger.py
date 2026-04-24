"""Structured JSON logging for all Aegis services.

Emits one JSON line per log event with stable field names:
    severity, time, service, trace_id, venue_id, incident_id, message, ...

Cloud Logging parses these automatically into structured log entries,
which means queries like:
    severity >= ERROR AND jsonPayload.incident_id = "INC-7741"
just work.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from aegis_shared.config import get_settings


def _add_service_name(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """Stamp every log with the service name for filtering in Cloud Logging."""
    event_dict.setdefault("service", "aegis")
    return event_dict


def _rename_event_to_message(
    logger: logging.Logger,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Cloud Logging prefers `message` over structlog's default `event`."""
    if "event" in event_dict:
        event_dict["message"] = event_dict.pop("event")
    return event_dict


def _rename_level_to_severity(
    logger: logging.Logger,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Cloud Logging uses `severity` (uppercase)."""
    if "level" in event_dict:
        event_dict["severity"] = event_dict.pop("level").upper()
    return event_dict


def setup_logging(service_name: str, level: str | None = None) -> None:
    """Configure structlog + stdlib logging once at service startup.

    Call from each service's main.py BEFORE any other import that logs.
    """
    settings = get_settings()
    resolved_level = (level or settings.aegis_log_level).upper()

    # Route stdlib logging through structlog's processors.
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=resolved_level,
        force=True,
    )

    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        _add_service_name,
        _rename_level_to_severity,
        _rename_event_to_message,
        structlog.processors.JSONRenderer(),
    ]

    # In local dev, prefer human-readable output.
    if settings.is_local:
        processors[-1] = structlog.dev.ConsoleRenderer(colors=True)  # type: ignore[assignment]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, resolved_level, logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Quiet down noisy libraries.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("google.auth").setLevel(logging.WARNING)

    structlog.contextvars.bind_contextvars(service=service_name)


def get_logger(name: str | None = None, **bindings: Any) -> structlog.stdlib.BoundLogger:
    """Return a logger, optionally pre-bound with keys (e.g. venue_id, incident_id)."""
    logger = structlog.get_logger(name)
    return logger.bind(**bindings) if bindings else logger
