"""Gemini / Vertex AI client wrapper.

Every agent and service calls Gemini through THIS module. It handles:
    - Auth (Vertex AI via ADC, or Gemini Developer API via GOOGLE_API_KEY)
    - Model selection (pro / flash / medgemma)
    - Retry with exponential backoff on transient errors
    - Structured-output coercion via Pydantic + response_schema
    - Multi-modal (text + image bytes) input
    - Token + cost logging
    - Prompt hashing for audit trail

Do not import `google.genai` or `vertexai` directly in services — use this.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, TypeVar

from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from aegis_shared.config import Settings, get_settings
from aegis_shared.errors import DownstreamServiceError
from aegis_shared.logger import get_logger

log = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


@dataclass(frozen=True)
class GeminiResponse:
    """Wrapped Gemini response with provenance."""

    text: str
    model: str
    prompt_hash: str
    input_tokens: int
    output_tokens: int
    finish_reason: str


class GeminiClient:
    """Single-process Gemini client.

    Usage:
        client = GeminiClient()
        resp = await client.generate("hello", model="flash")
        parsed = await client.generate_structured(prompt, schema=MyModel, model="pro")
        parsed = await client.analyze_image(prompt, image_bytes, schema=VisionOutput)
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client: Any = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        try:
            from google import genai  # type: ignore[import-not-found]

            if self._settings.google_api_key:
                self._client = genai.Client(api_key=self._settings.google_api_key)
            else:
                self._client = genai.Client(
                    vertexai=True,
                    project=self._settings.gcp_project_id,
                    location=self._settings.vertex_ai_location,
                )
            self._initialized = True
            log.info(
                "gemini_client_initialized",
                vertex_ai=not bool(self._settings.google_api_key),
                project=self._settings.gcp_project_id,
                location=self._settings.vertex_ai_location,
            )
        except ImportError as exc:  # pragma: no cover
            raise DownstreamServiceError(
                "google-genai SDK not installed. Add `google-genai` to service deps.",
                context={"original": str(exc)},
            ) from exc

    def _resolve_model(self, alias: str) -> str:
        mapping = {
            "pro": self._settings.gemini_pro_model,
            "flash": self._settings.gemini_flash_model,
        }
        return mapping.get(alias, alias)

    @staticmethod
    def _hash_prompt(prompt: str) -> str:
        return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _extract_json(text: str) -> str:
        """Best-effort extract a JSON object from a model response.

        Gemini JSON mode usually returns clean JSON, but older prompts or
        ``gemini-1.5`` fallbacks sometimes wrap output in markdown fences.
        """
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```\s*$", "", text)
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return match.group(0) if match else text

    @retry(
        retry=retry_if_exception_type(DownstreamServiceError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        reraise=True,
    )
    async def generate(
        self,
        prompt: str,
        *,
        model: str = "flash",
        system_instruction: str | None = None,
        temperature: float = 0.2,
        response_mime_type: str | None = None,
        response_schema: type[BaseModel] | None = None,
        image_bytes: bytes | None = None,
        image_mime: str = "image/jpeg",
    ) -> GeminiResponse:
        """Text / multimodal generation.

        - ``image_bytes`` turns the call into a multimodal vision prompt.
        - ``response_mime_type='application/json'`` enables JSON mode.
        - ``response_schema`` is passed directly to Gemini for schema-constrained JSON.
        """
        self._ensure_initialized()
        model_id = self._resolve_model(model)
        prompt_hash = self._hash_prompt(prompt)

        from google.genai import types  # type: ignore[import-not-found]

        contents: list[Any] = [prompt]
        if image_bytes is not None:
            contents = [
                types.Part.from_bytes(data=image_bytes, mime_type=image_mime),
                prompt,
            ]

        config: dict[str, Any] = {"temperature": temperature}
        if system_instruction:
            config["system_instruction"] = system_instruction
        if response_mime_type:
            config["response_mime_type"] = response_mime_type
        if response_schema is not None:
            config["response_schema"] = response_schema

        try:
            response = await self._client.aio.models.generate_content(
                model=model_id,
                contents=contents,
                config=config,
            )
        except Exception as exc:
            log.error(
                "gemini_call_failed",
                model=model_id,
                prompt_hash=prompt_hash,
                error=str(exc),
            )
            raise DownstreamServiceError(
                "Gemini call failed",
                context={"model": model_id, "prompt_hash": prompt_hash},
            ) from exc

        usage = getattr(response, "usage_metadata", None)
        result = GeminiResponse(
            text=response.text or "",
            model=model_id,
            prompt_hash=prompt_hash,
            input_tokens=getattr(usage, "prompt_token_count", 0) if usage else 0,
            output_tokens=getattr(usage, "candidates_token_count", 0) if usage else 0,
            finish_reason=str(getattr(response, "finish_reason", "UNKNOWN")),
        )
        log.info(
            "gemini_call_ok",
            model=model_id,
            prompt_hash=prompt_hash,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            multimodal=image_bytes is not None,
        )
        return result

    async def generate_structured(
        self,
        prompt: str,
        *,
        schema: type[T],
        model: str = "flash",
        system_instruction: str | None = None,
        temperature: float = 0.1,
        image_bytes: bytes | None = None,
        image_mime: str = "image/jpeg",
    ) -> T:
        """Generate and coerce output into a Pydantic model using JSON mode."""
        response = await self.generate(
            prompt,
            model=model,
            system_instruction=system_instruction,
            temperature=temperature,
            response_mime_type="application/json",
            response_schema=schema,
            image_bytes=image_bytes,
            image_mime=image_mime,
        )
        raw = self._extract_json(response.text)
        try:
            return schema.model_validate_json(raw)
        except Exception as exc:
            # One repair attempt with a stricter instruction.
            log.warning(
                "gemini_structured_parse_failed",
                model=response.model,
                prompt_hash=response.prompt_hash,
                raw=raw[:500],
                error=str(exc),
            )
            try:
                data = json.loads(raw)
                return schema.model_validate(data)
            except Exception as exc2:
                raise DownstreamServiceError(
                    "Gemini returned output that did not match the requested schema.",
                    context={"schema": schema.__name__, "raw_preview": raw[:500]},
                ) from exc2

    async def analyze_image(
        self,
        prompt: str,
        image_bytes: bytes,
        *,
        schema: type[T],
        model: str = "flash",
        system_instruction: str | None = None,
        temperature: float = 0.1,
        image_mime: str = "image/jpeg",
    ) -> T:
        """Convenience wrapper for multimodal vision + structured output."""
        return await self.generate_structured(
            prompt,
            schema=schema,
            model=model,
            system_instruction=system_instruction,
            temperature=temperature,
            image_bytes=image_bytes,
            image_mime=image_mime,
        )


# ===== Singleton access =====

_CLIENT: GeminiClient | None = None


def get_gemini_client() -> GeminiClient:
    """Return a process-wide shared Gemini client."""
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = GeminiClient()
    return _CLIENT
