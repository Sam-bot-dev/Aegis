"""Prompt registry.

Every agent prompt lives as a markdown file under ``/prompts/``. Agents load
them via the registry so we get:

    - one canonical place to edit prompts,
    - an SHA-256 hash attached to every Gemini call for audit trail,
    - a fallback search path that works both in local dev (running from the
      repo root) and in a deployed Cloud Run container (prompts shipped inside
      the image at ``/app/prompts/``).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from aegis_shared.errors import ConfigurationError
from aegis_shared.logger import get_logger

log = get_logger(__name__)


@dataclass(frozen=True)
class Prompt:
    name: str
    path: Path
    text: str
    hash: str  # SHA-256 prefix, suitable for audit

    @classmethod
    def from_path(cls, name: str, path: Path) -> Prompt:
        text = path.read_text(encoding="utf-8")
        return cls(
            name=name,
            path=path,
            text=text,
            hash=hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],
        )


_SEARCH_ROOTS: tuple[Path, ...] = (
    Path.cwd() / "prompts",
    Path("/app/prompts"),
    Path(__file__).resolve().parents[3] / "prompts",  # services/shared/aegis_shared/ → repo/prompts
    Path(__file__).resolve().parents[4] / "prompts",  # fallback for deeper layouts
)


def _resolve_prompt_path(name: str) -> Path:
    filename = f"{name}.md"
    for root in _SEARCH_ROOTS:
        candidate = root / filename
        if candidate.is_file():
            return candidate
    raise ConfigurationError(
        f"Prompt '{name}' not found in any search root.",
        context={"name": name, "searched": [str(r) for r in _SEARCH_ROOTS]},
    )


@lru_cache(maxsize=64)
def load_prompt(name: str) -> Prompt:
    """Load and cache a prompt by name (e.g. ``'vision_classifier'``)."""
    path = _resolve_prompt_path(name)
    prompt = Prompt.from_path(name=name, path=path)
    log.info("prompt_loaded", name=name, hash=prompt.hash, path=str(path))
    return prompt
