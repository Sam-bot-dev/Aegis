# ADR-0002: Vision service uses real Gemini with heuristic fallback

**Status:** Accepted · 2026-04-24 · Proposer: @ubaid

## Context

Phase 1 originally used a deterministic vision stub so the pipeline could be
wired quickly without waiting on model credentials. That helped bootstrap the
event flow, but it created three problems:

1. The architecture docs drifted away from the actual product story.
2. Judges expect to see real Google AI usage, not only scaffolding.
3. A stub cannot produce confidence-scored rationale or evidence that feels
   credible in the dashboard.

We already have a reusable `GeminiClient` in `services/shared/aegis_shared`.

## Decision

The Vision service will use Gemini 2.5 Flash for the synchronous
`POST /v1/analyze` path and return a structured `VisionClassification`
payload. If the Gemini call fails, times out, or credentials are missing, the
service falls back to a low-confidence heuristic classification so the vertical
slice remains demoable.

## Consequences

### Positive

- The Phase 1 demo now uses real multimodal reasoning.
- Prompt hashes and structured output are available for audit.
- The service remains resilient when Vertex or API credentials are unavailable.

### Negative / Accepted tradeoffs

- Model calls introduce cost and latency compared with a stub.
- Output can vary between runs, so smoke tests must validate schema, not a
  single hard-coded category.
- The event-driven Pub/Sub subscriber for `raw-frames` is still a gap even
  though the synchronous AI path is real.

### Review trigger

Re-open this ADR if:

- Gemini latency pushes the demo past acceptable UX thresholds
- We need a cheaper pre-filter before every frame reaches Gemini
- Another model materially outperforms Flash for the same cost envelope
