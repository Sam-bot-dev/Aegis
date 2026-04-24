# Load Tests

Current scaffold:

- `incident_pipeline_smoke.js` — k6 scenario that drives `POST /v1/handle`
  with a steady stream of synthetic perceptual signals

Example:

```bash
k6 run tests/load/incident_pipeline_smoke.js
```

Useful env vars:

- `ORCH_BASE_URL`
- `VENUE_ID`
- `INCIDENT_RATE`
- `DURATION`
- `PRE_ALLOCATED_VUS`
- `MAX_VUS`
