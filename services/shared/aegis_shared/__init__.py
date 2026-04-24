"""Aegis shared library.

Provides common utilities for all Aegis microservices:
    - config:    typed settings via pydantic-settings
    - logger:    structured JSON logging with trace context
    - gemini:    Vertex AI / Gemini client wrapper
    - firestore: Firestore client helper
    - pubsub:    Pub/Sub publisher/subscriber helpers
    - schemas:   Pydantic models for core Aegis entities
    - errors:    typed exception hierarchy
    - prompts:   markdown-backed prompt registry with hashing
    - audit:     append-only audit event emitter with SHA-256 chain
    - fcm:       Firebase Cloud Messaging helper for push notifications
"""

from aegis_shared.config import Settings, get_settings
from aegis_shared.errors import (
    AegisError,
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    DownstreamServiceError,
    InvalidInputError,
    NotFoundError,
    RateLimitedError,
    SafetyEnvelopeViolation,
)
from aegis_shared.logger import get_logger, setup_logging

__version__ = "0.1.0"

__all__ = [
    "AegisError",
    "AuthenticationError",
    "AuthorizationError",
    "ConfigurationError",
    "DownstreamServiceError",
    "InvalidInputError",
    "NotFoundError",
    "RateLimitedError",
    "SafetyEnvelopeViolation",
    "Settings",
    "__version__",
    "get_logger",
    "get_settings",
    "setup_logging",
]
