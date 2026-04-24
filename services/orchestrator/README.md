# `services/orchestrator`

Coordinates the multi-agent incident response. Phase 1 ships a deterministic
two-agent flow (classifier → dispatcher) so the full pipeline runs end-to-end
without Vertex AI credentials. Phase 2 replaces it with the real Vertex AI ADK
graph defined under `/agents`.

## Endpoint

`POST /v1/handle` takes a `PerceptualSignal` and returns the resulting
`Incident`, `IncidentClassification`, and whether a dispatch was triggered.
Under the hood it publishes to `incident-events` and (when warranted) to
`dispatch-events`.

## Run

```bash
make orchestrator   # :8003
```
