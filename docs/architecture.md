# Aegis — Architecture

> This document is the canonical reference for the system. When this disagrees
> with any other doc, this wins (and open a PR to fix the other one).

---

## 1. One-slide mental model

Aegis turns a mass-gathering venue into a *self-monitoring, self-coordinating*
emergency response system. Every camera, sensor, and staff phone becomes a
sensor. A multi-agent orchestrator running on Vertex AI reasons over those
signals, decides what is happening, and drives a coordinated response in
under 60 seconds.

**Single metric we optimize for:** Dispatch Latency (DL) — time from first
perceptual signal to responder en-route with correct brief. Baseline in India
is 12–18 minutes; our target is p95 ≤ 60s.

---

## 2. Layer diagram (production, Phase 2+)

```
┌────────────────────────────────────────────────────────────────────┐
│                    EDGE / VENUE PREMISES                            │
│  CCTV cams · IoT sensors · Staff phones · Guest phones · PA system │
│                                                                     │
│  [Aegis Edge Gateway]  (optional; runs on-prem for latency)        │
│   - RTSP relay · Frame sampler · Audio pre-proc · Local buffer     │
└──────────┬──────────────────────────────────────────────────────────┘
           │ TLS 1.3 / mTLS · HLS video · MQTT sensors
           ▼
┌────────────────────────────────────────────────────────────────────┐
│                     GCP INGESTION LAYER                             │
│   [Cloud Run: Ingest] → Cloud Storage + Pub/Sub (raw topics)       │
│   Auth via Firebase App Check · Rate limited via Cloud Armor       │
└──────────┬──────────────────────────────────────────────────────────┘
           │ Pub/Sub
           ▼
┌────────────────────────────────────────────────────────────────────┐
│                     PERCEPTION LAYER                                │
│   [Vision Svc]   [Audio Svc]   [Sensor Fusion Svc]                 │
│   Gemini 2.5     Gemini Audio  Spatio-temporal coalescence         │
│   Vision         + STT fallback                                     │
│   DLP redaction pre-persist on every frame                         │
└──────────┬──────────────────────────────────────────────────────────┘
           │ Pub/Sub: perceptual-signals
           ▼
┌────────────────────────────────────────────────────────────────────┐
│            ORCHESTRATION LAYER (Vertex AI Agent Engine + ADK)      │
│                                                                     │
│         ┌─────────── ORCHESTRATOR AGENT ──────────┐                 │
│         │  ReAct loop · state machine · audit     │                 │
│         └──┬─────┬──────┬─────────┬────────┬──────┘                 │
│            ▼     ▼      ▼         ▼        ▼                        │
│      [Classifier][Cascade][Triage][Dispatch][Evacuation]            │
│                              │ MedGemma                             │
└──────────┬──────────────────────────────────────────────────────────┘
           │ Pub/Sub: incident-events · dispatch-events
           ▼
┌────────────────────────────────────────────────────────────────────┐
│                       ACTION LAYER                                  │
│   [Dispatch Svc]  [Comms Svc]   [Routing]   [Authority Svc]        │
│   FCM pushes ·    Translate +   Maps Routes ·  Signed webhooks     │
│   escalation      TTS · PA API  Indoor graph  JSON-LD packets      │
└──────────┬──────────────────────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────────────────┐
│                  STATE · AUDIT · ANALYTICS                          │
│   Firestore (live state)  BigQuery (audit, append-only, hashed)    │
│   Cloud Storage (evidence, CMEK)  Matching Engine (skill vectors)  │
└──────────┬──────────────────────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────────────────┐
│                       PRESENTATION                                  │
│   Staff (Next.js PWA)  Responder (Next.js PWA)  Guest PWA  Venue Dashboard │
│   Authority Console                                                 │
└────────────────────────────────────────────────────────────────────┘
```

---

## 3. Phase 1 simplification (what's in the repo right now)

For the April 24 submission we run a vertical slice of the above:

```
HTTP POST frame → Ingest (:8001)
                    │ publishes to raw-frames
                    ▼
                  Vision (:8002)  ← synchronous /v1/analyze for demo
                    │ returns PerceptualSignal
                    ▼
                Orchestrator (:8003)
                    │ classifies + publishes incident-events
                    │ + dispatch-events if S1/S2
                    ▼
                  Dispatch (:8004)  ← ack/enroute/arrived state machine
```

All four services are runnable today. Pub/Sub runs on the local emulator.
Firestore writes are already wired into the Orchestrator and Dispatch flows,
with emulator-friendly soft-fail behavior during local development.

The Vision demo path now calls real Gemini 2.5 Flash through
`aegis_shared.gemini` and emits a structured `PerceptualSignal`. When Gemini
credentials are unavailable or the model call fails, the service falls back to
a low-confidence heuristic classification so the vertical slice still runs.
The remaining gap is the push subscriber for `raw-frames`, not the Gemini path.

---

## 4. Service catalog

| Service       | Port | Stack               | Responsibility                                 |
| ------------- | ---- | ------------------- | ---------------------------------------------- |
| ingest        | 8001 | FastAPI · Python    | Accept frames / sensors, publish raw topics    |
| vision        | 8002 | FastAPI · Gemini    | Classify frames → emit PerceptualSignal        |
| orchestrator  | 8003 | FastAPI · ADK       | Run agent graph, drive incident lifecycle      |
| dispatch      | 8004 | FastAPI · FCM       | Page responders, track ack state               |
| audio         | 8005 | Phase 2             | Audio event detection                          |
| fusion        | 8006 | Phase 2             | Sensor-fusion coalescence                       |
| triage        | 8007 | Phase 2 · MedGemma  | Medical acuity + pre-hospital instructions     |
| evacuation    | 8008 | Phase 2             | Flow-aware evacuation routing                  |
| comms         | 8009 | Phase 2             | Multi-lingual guest comms                      |
| authority     | 8010 | Phase 2             | Signed webhooks to civic authorities           |
| analytics     | 8011 | Phase 2             | BigQuery dashboards                            |
| audit         | 8012 | Phase 2             | Append-only audit writer + integrity verifier  |

---

## 5. Pub/Sub topic inventory

All schemas under `/pubsub-schemas/`. Ordering key in parentheses.

| Topic                | Producer             | Consumer(s)                    | Ordering                   |
| -------------------- | -------------------- | ------------------------------ | -------------------------- |
| raw-frames           | Ingest               | Vision                         | `venue_id:camera_id`       |
| audio-chunks         | Ingest               | Audio                          | `venue_id:mic_id`          |
| sensor-events        | Ingest (via MQTT)    | Fusion                         | `venue_id:sensor_id`       |
| perceptual-signals   | Vision · Audio · Fusion | Orchestrator                | `venue_id`                 |
| incident-events      | Orchestrator         | Dispatch · Audit · UI sync     | `venue_id:incident_id`     |
| dispatch-events      | Orchestrator         | Dispatch Svc                   | `venue_id:incident_id`     |
| evacuation-events    | Evacuation Agent     | Comms · UI broadcast           | `venue_id:incident_id`     |
| authority-events     | Authority Agent      | External webhook worker        | `venue_id:incident_id`     |
| audit-events         | All                  | BigQuery sink                  | `venue_id:incident_id`     |
| learning-examples    | Post-incident Agent  | Vertex AI Pipelines            | `venue_id`                 |

---

## 6. Data plane

### Firestore (live, UI-reactive)

Primary collections: `venues`, `incidents`, `users`. Subcollections carry
cameras, sensors, staff, responders, chat, and per-incident signals /
dispatches / events / triage / evacuation / overrides. Schemas in
`services/shared/aegis_shared/schemas.py`, rules in
`firebase/firestore.rules`, indexes in `firebase/firestore.indexes.json`.

### BigQuery (audit + analytics + learning)

Three datasets: `aegis_audit`, `aegis_analytics`, `aegis_learning`. The
audit table is append-only with a row-level SHA-256 hash chain; the daily
integrity verifier job catches any tampering.

### Cloud Storage buckets

- `aegis-evidence-<env>` — raw + DLP-redacted frames / clips. CMEK-encrypted.
- `aegis-reports-<env>` — generated PDF reports. 7-year retention.
- `aegis-venue-assets-<env>` — floor plans, logos.
- `aegis-models-<env>` — custom fine-tuned weights.

---

## 7. Agent graph

Agents are defined under `/agents/<name>/` and deployed to Vertex AI Agent
Engine. Each has a versioned prompt in `/prompts/<name>.md`. The
Orchestrator is the top-level ReAct agent that invokes the rest as tools.

```
                    Orchestrator (Gemini 2.5 Pro)
                    │
    ┌───────────────┼─────────────┬──────────────┬─────────────┐
    ▼               ▼             ▼              ▼             ▼
Classifier     Cascade         Triage         Dispatcher    Evacuation
(Flash)        (Pro + venue   (MedGemma)     (Flash +      (Pro + graph
               graph context)                  LP solver +   solver)
                                               Gemini re-
                                               rank)
                    │
                    ▼
             Comms · Authority Reporter · Post-Incident Report
```

Novel contributions (§10 of the blueprint):

1. **Cascade-aware classifier** — two-stage model predicting 30s/90s/300s
   outcome probabilities, not just current state
2. **Triage-constrained dispatcher** — hybrid integer-LP solver + Gemini
   re-rank over the top-3 candidates
3. **Privacy-preserving guest-phone fusion** — on-device feature
   extraction, only event labels upload
4. **Post-incident learning loop** — every resolved incident feeds LoRA
   fine-tuning; accuracy curve visible on the dashboard
5. **Flow-aware evacuation routing** — min-cost max-flow over indoor
   graph, real-time density-aware rerouting

---

## 8. Security envelope

- **Auth:** Firebase Auth (phone OTP for staff, email+MFA for corporate,
  SSO for authority)
- **RBAC:** Firebase custom claims carry `role` + `venues[]` + `skills[]`;
  enforced in Firestore rules, backend middleware, and UI
- **App integrity:** Firebase App Check on every client call
- **At-rest:** default encryption everywhere, CMEK on evidence bucket
- **In-transit:** TLS 1.3; mTLS between edge gateway and Ingest
- **PII:** Cloud DLP redaction before any human review of frames or
  transcripts
- **Audit:** every agent decision and human override logged to an
  append-only, hash-chained BigQuery table

---

## 9. Human-in-the-loop safety

Default mode is **co-pilot**, not autonomous. All external side-effects
(dispatching 108 ambulance, triggering PA announcement) are gated on an
operator acknowledge within 15 seconds. Venue management can opt in to
autonomous mode for S1 incidents only after a configured drill history.

Every agent call carries a confidence score. Below a threshold the decision
is routed to a human. Every override is recorded with its reason.

---

## 10. Where to go from here

- **Running it** → `SETUP.md`
- **Building Phase 1 features** → `README.md` (repo map) and the blueprint §87
- **Adding an agent** → `prompts/README.md` and `agents/<name>/README.md`
- **Writing a decision record** → `docs/decisions/` (example: ADR-0001)
