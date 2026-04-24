"""Aegis exception hierarchy.

Every service raises typed errors that map cleanly to HTTP codes and audit
categories. Catching `AegisError` at a service boundary is always safe.
"""

from __future__ import annotations


class AegisError(Exception):
    """Base for all Aegis exceptions."""

    http_status: int = 500
    audit_category: str = "internal_error"

    def __init__(self, message: str, *, context: dict[str, object] | None = None) -> None:
        super().__init__(message)
        self.context = context or {}


class ConfigurationError(AegisError):
    """Raised when required config is missing or invalid at startup."""

    http_status = 500
    audit_category = "configuration_error"


class InvalidInputError(AegisError):
    """Raised when a caller supplies malformed input."""

    http_status = 400
    audit_category = "invalid_input"


class AuthenticationError(AegisError):
    http_status = 401
    audit_category = "authentication_error"


class AuthorizationError(AegisError):
    http_status = 403
    audit_category = "authorization_error"


class NotFoundError(AegisError):
    http_status = 404
    audit_category = "not_found"


class DownstreamServiceError(AegisError):
    """Raised when an external/downstream dependency fails (Gemini, Firestore, etc.)."""

    http_status = 502
    audit_category = "downstream_error"


class RateLimitedError(AegisError):
    http_status = 429
    audit_category = "rate_limited"


class SafetyEnvelopeViolation(AegisError):
    """Raised when an agent tries to take an action not permitted by its safety envelope.

    E.g. triggering a real 108 dispatch from a drill run, or attempting medical
    direction without a credentialed responder in the loop.
    """

    http_status = 403
    audit_category = "safety_envelope_violation"
