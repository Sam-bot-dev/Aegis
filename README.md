# Aegis

> *An agentic AI platform that turns any mass gathering — hotel, wedding, religious gathering, conference — into a self-monitoring, self-coordinating emergency response system.*

**Team:** Better Call Coders · **Event:** Google Solution Challenge 2026 · **Theme:** Rapid Crisis Response (Open Innovation)

---

## Start here

**If you haven't set up your Google Cloud / Firebase / local tools yet → read [`SETUP.md`](./SETUP.md) first.** Nothing in this repo will run until that's done.

Once setup is complete, start the local dev stack:

```bash
make dev       # starts Firestore + Pub/Sub emulators + all Python services
make test      # runs unit tests for all Python services
make lint      # ruff + mypy + eslint
```

---

## Repo map

```
/services           Python microservices (FastAPI on Cloud Run)
  /shared             shared library: config, logger, clients (Gemini, Firestore, Pub/Sub)
  /ingest             HTTPS ingest for frames/audio/sensor events
  /vision             Gemini Vision analyzer
  /orchestrator       Vertex AI ADK multi-agent orchestrator
  /dispatch           Responder paging + escalation ladder

/agents             ADK agent definitions (Python)
/apps               Client apps (Flutter + Next.js — init after SETUP.md)
/packages           Shared packages (schemas, UI libs)
/firebase           Firestore rules, indexes, Cloud Functions
/pubsub-schemas     Protobuf + JSON Schema for event topics
/prompts            Versioned agent prompts (.md)
/terraform          Infrastructure as Code (Phase 2)
/scripts            Dev + deploy scripts
/docs               Architecture, ADRs, user research
/tests              E2E + load tests
```

## Architecture at a glance

```
Edge (CCTV, sensors, phones)
      │
      ▼
[Ingest] → Pub/Sub → [Vision / Audio / Fusion]
                           │
                           ▼
                   Pub/Sub: perceptual_signals
                           │
                           ▼
                 [Orchestrator Agent (Vertex AI ADK)]
                    │ │ │ │ │
      ┌─────────────┘ │ │ │ └─────────────┐
      ▼               ▼ ▼ ▼               ▼
 [Classifier]  [Triage] [Dispatch] [Evacuation] [Comms]
                           │
                           ▼
              FCM / WebHooks / PA / BigQuery audit
                           │
                           ▼
         Staff / Responder / Dashboard / Authority apps
```

Full spec in [`docs/architecture.md`](./docs/architecture.md) and the root-level blueprint document.

## Success metric

We optimize for **Dispatch Latency (DL)** — time from first perceptual signal to responder en-route with correct brief. Industry baseline is 12–18 min. Our target is **p95 ≤ 60s**.

---

## Contributing

1. Branch off `main` as `feat/<area>/<short-desc>`
2. Run `make lint test` before pushing
3. Open PR → CI must be green → 1 review → merge
4. No direct commits to `main`

---

Licensed under Apache 2.0 for platform code. Prompts and fine-tuning datasets are proprietary.
