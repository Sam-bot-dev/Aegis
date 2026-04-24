# `services/vision`

Consumes camera frames → Gemini Vision → emits perceptual signals for the
Orchestrator to reason over.

## Phase 1 (current)

The synchronous `/v1/analyze` endpoint now calls real Gemini Vision and falls
back to a low-confidence heuristic classification if credentials are missing or
the model call fails.

The async `/pubsub/raw-frames` endpoint is also live. It accepts a Pub/Sub push
envelope from the `raw-frames` topic, validates the payload, and republishes a
`PerceptualSignal` for the Orchestrator.

## Phase 2 plan

- Add motion pre-filtering and dedup so Gemini is not called on static frames
- Store redacted evidence to Cloud Storage and populate `evidence_uri`
- Add privacy redaction before any human review path

## Run

```bash
make vision   # :8002
```
