"""Aegis agent suite.

Each sub-module exposes a single class whose name ends in ``Agent``. In Phase 1
these are plain async Python classes that call Gemini through ``aegis_shared``.
Phase 2 re-wraps them as Vertex AI ADK agents so the orchestrator can run them
as tools inside an Agent Engine session.
"""
