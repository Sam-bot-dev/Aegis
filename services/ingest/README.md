# `services/ingest`

Thin, high-availability HTTPS edge that receives frames / audio / sensor events
from the venue's edge gateway and publishes them onto Pub/Sub. No heavy work
happens here — that's by design.

## Endpoints

| Method | Path         | What it does                                |
| ------ | ------------ | ------------------------------------------- |
| GET    | /health      | Liveness                                     |
| GET    | /ready       | Readiness                                    |
| POST   | /v1/frames   | Accept a single JPEG frame (multipart)       |
| POST   | /v1/sensors  | Accept a batch of sensor readings (JSON)     |

Interactive docs at `/docs` when the service is running.

## Run locally

```bash
make emulators         # in one terminal
make ingest            # in another; runs on :8001
curl http://localhost:8001/health
```

## Test

```bash
pytest services/ingest/tests -v
```

## Deploy (Phase 2)

`gcloud run deploy aegis-ingest --source . --region asia-south1`
