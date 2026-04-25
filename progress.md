# Aegis — Master Progress Tracker
### Better Call Coders · Google Solution Challenge 2026

> **Single source of truth for build state.** Every entry below was verified by reading the actual file.
> Any codex or developer building this project should read this file first, then the blueprint.
> Last full audit: **2026-04-24**

---

## Legend
- `[x]` — done, verified working code in repo
- `[~]` — scaffolded / partial — file exists but real logic is missing or incomplete
- `[ ]` — not started — no file, empty directory, or placeholder only

Priority labels match blueprint §7: **(P0)** must ship Phase 1 · **(P1)** Product Vault · **(P2)** Grand Finale · **(P3)** stretch

---

---

# ═══════════════════════════════════════════════
# PHASE 0 — REPOSITORY & LOCAL SETUP
# ═══════════════════════════════════════════════

## Repo skeleton
- [x] Full monorepo folder tree exists: `apps/ services/ agents/ packages/ prompts/ pubsub-schemas/ terraform/ tests/ docs/ firebase/ monitoring/ scripts/`
- [x] `pyproject.toml` — root tooling config: ruff (full ruleset E/F/W/I/B/UP/N/S/A/C4/SIM/RET/PL/RUF), mypy strict mode, pytest config with asyncio_mode=auto, coverage fail_under=70
- [x] `requirements.txt` — top-level deps
- [x] `Makefile` — targets: `setup`, `install`, `emulators`, `dev`, `stop`, `ingest`, `vision`, `orchestrator`, `dispatch`, `lint`, `fmt`, `test`, `clean`
- [x] `docker-compose.yml` — Firestore emulator (:8080), Pub/Sub emulator (:8085), Redis (:6379); health check on Firestore
- [x] `.env.example` — all env vars documented
- [x] `.env` — populated with real values
- [x] `.secrets/service-account.json` + `.secrets/firebase-adminsdk.json`
- [x] Python 3.13 venv at `.venv/`
- [x] `scripts/dev.ps1` + `scripts/dev.sh` — starts all 4 services in separate windows, loads .env
- [x] `scripts/smoke.ps1` + `scripts/smoke.sh` — 5-step end-to-end smoke test (health → ingest frame → vision classify → orchestrator handle → dispatch state machine)
- [x] Firebase project linked (`firebase use aegis-gsc-2026`)
- [x] `firebase/firestore.rules` — full RBAC (venue membership via custom claims, role guards, dispatch update restricted to assigned responder, default-deny catch-all)
- [x] `firebase/firestore.indexes.json` — 4 composite indexes: incidents(venue_id+status+detected_at), incidents(venue_id+detected_at), dispatches(responder_id+status+paged_at), events(venue_id+event_time)
- [x] `prompts/vision_classifier.md` — full few-shot prompt with JSON schema, 7 rules, 3 examples (kitchen fire, nominal, crowd surge)
- [x] `prompts/orchestrator.md` — full system prompt with tool catalog, non-negotiable rules, calibration thresholds, tone rules
- [x] `pubsub-schemas/` — 5 JSON schema files: `raw_frame`, `perceptual_signal`, `incident_event`, `dispatch_event`, `sensor_event` + README
- [x] `docs/architecture.md` — full layer diagram, service catalog (14 services), Pub/Sub topic inventory, novel contributions list
- [x] `docs/decisions/0001-core-technology-stack.md` — ADR exists
- [x] `README.md` — repo map, architecture diagram, success metric, contributing guide
- [x] `SETUP.md` — first-time setup guide
- [x] `CONTRIBUTING.md` — branch naming, PR flow

## Not done in Phase 0
- [ ] `LICENSE` — Apache 2.0 / MIT split not applied (blueprint closing checklist item)
- [x] `.pre-commit-config.yaml` — pre-commit hooks configured for ruff, mypy, gitleaks, prettier, and eslint entrypoints
- [x] `.github/workflows/` — CI + deploy workflow scaffolds present (`ci.yml`, `deploy.yml`)
- [ ] `terraform/` — directory exists but **empty** — no IaC
- [ ] `firebase/functions/` — directory exists but **empty** — no Cloud Functions
- [ ] `packages/schemas/` — directory exists but **empty** — no generated types
- [ ] `monitoring/alerts/` — directory exists but **empty**
- [ ] `monitoring/dashboards/` — directory exists but **empty**
- [~] `tests/e2e/` — Playwright smoke scaffold added (`dashboard-smoke.spec.ts`); not executed yet
- [~] `tests/load/` — k6 scaffold added (`incident_pipeline_smoke.js`); target-scale validation still pending
- [ ] `docs/user-research/` — directory exists but **empty**

---

---

# ═══════════════════════════════════════════════
# PHASE 1 — VERTICAL SLICE MVP  (deadline 2026-04-24)
# ═══════════════════════════════════════════════

## ─── Shared Library `services/shared/aegis_shared` ───

### Fully implemented [x]
- [x] `__init__.py` — barrel export of all public symbols; `__version__ = "0.1.0"`
- [x] `config.py` — `Settings` (pydantic-settings): all env vars typed, emulator detection (`using_firestore_emulator`, `using_pubsub_emulator`), `is_local`, `is_prod` properties, `@lru_cache` singleton
- [x] `errors.py` — full typed exception hierarchy: `AegisError` (base), `ConfigurationError`, `InvalidInputError`, `AuthenticationError`, `AuthorizationError`, `NotFoundError`, `DownstreamServiceError`, `RateLimitedError`, `SafetyEnvelopeViolation` — each has `http_status` + `audit_category`
- [x] `logger.py` — structlog JSON logging: Cloud Logging field names (`severity`, `message`, `service`), local dev uses ConsoleRenderer, `setup_logging(service_name)` called at startup, `get_logger()` with optional pre-bound keys, noisy library suppression
- [x] `schemas.py` — complete Pydantic v2 models:
  - Enums: `IncidentCategory`, `Severity`, `IncidentStatus`, `DispatchStatus`, `SignalModality`, `ResponderSkill`
  - Geo: `GeoPoint`, `ZoneRef`
  - Vision: `BoundingBox`, `VisionEvidence`, `VisionClassification`
  - Signals: `PerceptualSignal`
  - Incidents: `CascadePrediction`, `IncidentClassification`, `Incident`, `IncidentEvent`
  - Dispatch: `Dispatch`, `DispatchEvent`
  - Audit: `AuditEvent`
  - Helpers: `utc_now()`, `new_id(prefix)`
- [x] `pubsub.py` — `publish_json()`: Pydantic/dict serialization, ordering keys (disabled on emulator with warning), `@lru_cache` publisher singleton, typed `PublishResult`, `topic_path()` helper
- [x] `gemini.py` — `GeminiClient`: Vertex AI (ADC) or Developer API (GOOGLE_API_KEY) init, `generate()` text + multimodal, `generate_structured()` JSON mode + Pydantic coercion with repair attempt, `analyze_image()` convenience wrapper, exponential-backoff retry via tenacity (3 attempts, 0.5–4s), prompt hashing (SHA-256 prefix), token counting, `GeminiResponse` dataclass, `get_gemini_client()` singleton
- [x] `firestore.py` — async `AsyncClient` (emulator-aware), `upsert_incident()`, `upsert_dispatch()` (with correct timestamp fields per status), `append_incident_event()`, `get_responders_for_venue()` — all soft-fail with warning log if Firestore unreachable; **actively used by orchestrator and dispatch services**
- [x] `audit.py` — full SHA-256 hash chain: `prev_hash` + `row_hash` over canonical JSON, `asyncio.Lock` for monotonic chain under concurrency, dual sink (BigQuery streaming insert + local `.audit/aegis_audit.jsonl` fallback), `write_audit()` async public API, `verify_chain_local()` for integrity CLI, `hash_object()` helper
- [x] `fcm.py` — Firebase Admin SDK init (cert path or ADC), `send_to_tokens()` with Android high-priority + APNS config (sound, vibration, content-available), `send_to_topic()` for venue staff topics, soft-fail if SDK missing
- [x] `prompts.py` — `PromptRegistry`: multi-path resolution (`cwd/prompts`, `/app/prompts`, repo-relative), `@lru_cache`, `Prompt` dataclass with SHA-256 hash for audit, `load_prompt(name)` public API

### Gaps in shared library
- [ ] `prompts/triage.md` — triage agent prompt not written (P1)
- [x] `prompts/cascade_predictor.md` — extracted from agent.py, loaded via `PromptRegistry`, prompt_hash logged on every call
- [x] `prompts/classifier.md` — extracted from agent.py, loaded via `PromptRegistry`, prompt_hash logged on every call
- [x] `prompts/dispatcher_rerank.md` — extracted from agent.py, loaded via `PromptRegistry`, prompt_hash logged on every call
- [x] `auth.py` helper — Firebase ID token verification + App Check token validation available as a FastAPI `Depends(verify_request)`. Local/dev mode short-circuits; `AEGIS_REQUIRE_AUTH=1` forces enforcement. Wire into each service in a follow-up PR.

---

## ─── Ingest Service `services/ingest` ─── (P0)

### Done
- [x] FastAPI app with `asynccontextmanager` lifespan, CORS middleware (open for demo), health endpoint `GET /health`
- [x] `routers/frames.py` — `POST /v1/frames`: multipart JPEG upload (max 5MB), `venue_id` + `camera_id` form fields, base64 inline payload, publishes to `raw-frames` with `venue_id:camera_id` ordering key + attributes, returns `FrameAckResponse` with `frame_id`
- [x] `routers/sensors.py` — `POST /v1/sensors`: batch `SensorReading` (up to 500), sensor types: smoke/co/heat/motion/door/panic_button, publishes one `sensor-events` message per reading with `venue_id:sensor_id` ordering key
- [x] `routers/health.py` — health router (inferred from import)

### Missing
- [ ] `POST /v1/audio` — audio chunk ingest router does not exist (P1)
- [ ] App Check token validation middleware — not implemented (P1)
- [ ] Cloud Storage write of raw frames before Pub/Sub publish (currently inline base64 in message — not scalable, will break at ~10MB frames) (P1)
- [ ] mTLS validation for edge gateway connections (P2)
- [ ] Rate limiting per venue_id (P1)

---

## ─── Vision Service `services/vision` ─── (P0)

### Done
- [x] FastAPI app with lifespan, health endpoint `GET /health`
- [x] `POST /v1/analyze` — **real Gemini 2.5 Flash multimodal call** via `GeminiClient.analyze_image()` using `prompts/vision_classifier.md` loaded via `PromptRegistry`; returns structured `VisionClassification` (category, sub_type, confidence, evidence with bounding boxes, rationale); publishes `PerceptualSignal` to `perceptual-signals` topic; `used_gemini` flag in response
- [x] Graceful fallback to `_HEURISTIC_FALLBACK` (OTHER / conf=0.05) on `DownstreamServiceError` — pipeline stays green without Gemini creds
- [x] `prompt_hash` logged in response for audit trail
- [x] `AnalyzeRequest` validates base64 input; rejects empty frames

### Missing
- [x] `POST /pubsub/raw-frames` Pub/Sub push subscriber — implemented and covered by service tests; event-driven Ingest → Pub/Sub → Vision path now exists
- [ ] Motion pre-filter — skip frames with <5% pixel change vs previous frame (cost saving — Gemini calls ~$0.002 each) (P1)
- [ ] Cloud DLP redaction of PII (faces, license plates, IDs) before storing evidence frame (P1)
- [ ] Cloud Storage write of redacted frame → populate `evidence_uri` on `PerceptualSignal` (P1)
- [ ] Memorystore Redis dedup cache — skip analyze if same `venue_id:camera_id:frame_hash` seen in last 2s (P1)
- [ ] Adaptive frame rate — escalate from 1fps to 5fps on detection confidence >0.5 (P2)
- [ ] Low-light frame enhancement preprocessing (P2)

---

## ─── Orchestrator Service `services/orchestrator` ─── (P0)

### Done
- [x] FastAPI app with lifespan, health endpoint
- [x] `POST /v1/handle` — single `PerceptualSignal` wrapper; delegates to handle-batch
- [x] `POST /v1/handle-batch` — full pipeline: resolve responders (Firestore or demo roster) → `OrchestratorAgent.run()` → upsert incident + classified event to Firestore → publish `incident-events` → for each dispatched responder: upsert dispatch to Firestore + publish `dispatch-events`; returns `HandleResponse` with result + dispatched flag + reasoning string
- [x] `POST /pubsub/perceptual-signals` — Pub/Sub push subscriber: base64 decode → validate → handle-batch
- [x] Demo responder roster baked in: Priya (duty manager), John (fire warden), Dr. Kavya (on-call doctor), Arjun (security) — used when Firestore returns no responders
- [x] Firestore: all writes (upsert_incident, append_incident_event, upsert_dispatch) wired
- [x] Pub/Sub: both `incident-events` and `dispatch-events` published with ordering keys
- [x] Audit events at: incident.detected, incident.classified, incident.cascade_predicted, incident.dispatched

### Missing
- [x] Drill-mode flag check — orchestrator service now reads `req.drill_mode` / `venue_context.drill_mode`, writes a `incident.drill_mode_enabled` audit event, stamps `drill=true` on every dispatch-events payload, and returns `drill_mode` + `external_webhooks_fired` on the HandleResponse so the HTTP layer and UI know the agent ran in isolation.
- [x] Autonomous-mode gate — when severity is S1 but `venue_context.autonomous_mode` is false and we're not in drill mode, the agent trace notes the S1 human-gate without firing external side effects.
- [ ] Human-in-the-loop 15s co-pilot gate before S1 auto-dispatch still relies on the staff-app acknowledge flow (P1 — needs operator explicit confirm UI next to the dispatch)
- [ ] `SafetyEnvelopeViolation` actively raised when an action attempts to violate drill mode (currently we suppress via gating; follow-up will surface a loud error on policy breach) (P1)
- [ ] Vertex AI ADK-native agent graph (ReAct loop, tool-use protocol, Agent Engine deploy) — current impl is direct Python async calls, not ADK (P2)
- [x] Auth middleware primitive available in `aegis_shared.auth.verify_request` — not yet mounted on every endpoint, but importable so services add `Depends(verify_request)` with a one-line change (P1 for mount, shared helper complete)

---

## ─── Dispatch Service `services/dispatch` ─── (P0)

### Done
- [x] `POST /v1/dispatches` — creates dispatch, sends FCM push via `send_to_tokens()`, arms 15s ack timeout via `asyncio.create_task`, calls `write_audit(dispatch.paged)`
- [x] `POST /v1/dispatches/{id}/ack` — cancels timeout, transitions to ACKNOWLEDGED, upserts Firestore with `acknowledged_at`, audit event
- [x] `POST /v1/dispatches/{id}/enroute` — same pattern, `en_route_at`
- [x] `POST /v1/dispatches/{id}/arrived` — same, `arrived_at`
- [x] `POST /v1/dispatches/{id}/handoff` — same, `handed_off_at`
- [x] `POST /v1/dispatches/{id}/decline` — cancels timeout, DECLINED, audit
- [x] `GET /v1/dispatches/{id}` — reads from in-memory dict, 404 if not found
- [x] `POST /pubsub/dispatch-events` — Pub/Sub push subscriber: only acts on `to_status=PAGED`; calls create_dispatch with FCM tokens from payload
- [x] Firestore persistence on every transition via `upsert_dispatch()`
- [x] Audit on every transition (`write_audit`)
- [x] FCM high-priority push with deep link `aegis://incident/{id}` on create
- [x] `_arm_timeout()` / `_cancel_timeout()` with asyncio task tracking

### Missing
- [~] **In-memory state is not safe across restarts or multiple Cloud Run instances** — GET now falls back to Firestore on memory misses, but transitions/timeouts are still memory-backed and not durable across restart (P0 before deploy)
- [ ] Auto-escalate to backup ladder on timeout — currently marks `TIMED_OUT` but does NOT page the next responder in the backup list (P1)
- [ ] Cloud Tasks for durable 15s timeout — `asyncio.create_task` is killed when the instance scales down (P1)
- [ ] RBAC middleware (P1)

---

## ─── Agents `agents/` ───

### Fully implemented
- [x] `agents/orchestrator/agent.py` — `OrchestratorAgent`: creates `Incident`, runs `ClassifierAgent` → parallel `CascadeAgent` + `DispatcherAgent` (for S1/S2), `write_audit` at every step, returns `OrchestratorOutput` (incident, classification, cascade, dispatch, agent_trace list)
- [x] `agents/classifier/agent.py` — `ClassifierAgent`: Gemini 2.5 Flash with full SYSTEM_PROMPT (severity rubric, 6 rules), `ClassifierInput.describe()` formats all signals as structured text, structured output `ClassifierOutput` (category/sub_type/severity/confidence/rationale/cascade_predictions), deterministic rule-based fallback (`_rule_based()`) for CI/no-creds
- [x] `agents/dispatcher/agent.py` — `DispatcherAgent`: hard filter (skill match, on_shift, credential_valid, max ETA), composite score (0.5×ETA + 0.3×skill + 0.1×lang + 0.1×workload_penalty), Gemini Flash rerank of top-3 for S1/S2 via `_GeminiRerank` structured output, primary N (2 for S1, 1 for S2) + backup ladder, `ResponderRecord` dataclass
- [x] `agents/cascade/agent.py` — `CascadeAgent`: Gemini 2.5 Pro with SYSTEM_PROMPT requesting 30/90/300s predictions + recommended_preemptive_actions, `CascadeOutput` with predictions list + actions list + rationale, `_heuristic_cascade()` fallback per incident category (FIRE/STAMPEDE/MEDICAL)

### Scaffolded (README only, no agent.py)
- [~] `agents/triage/` — README describes MedGemma ESI 1-5, approved-phrase library, safety envelope, output schema, 5-step Phase 2 build order. **No agent.py.** (P1)
- [~] `agents/comms/` — README describes 5 output types (PA announcement, FCM push, staff briefing, authority JSON-LD, next-of-kin SMS), 5-language list, tone rules. **No agent.py.** (P1)
- [~] `agents/evacuation/` — README describes min-cost max-flow over indoor graph, why flow-balanced beats shortest-path, demo path (bottleneck vs dispersed), 5-step Phase 2 build order. **No agent.py.** (P1)

### Not started
- [ ] `agents/post_incident/` — Sendai-format retrospective report (P2)
- [ ] `agents/learning_loop/` — resolved incident → training example (P2)

---

## ─── Frontend Apps ───

### Staff app `apps/staff` — Next.js 14 PWA (Phase 1 pivot from Flutter)

#### Done
- [x] Next.js 14 app router, TypeScript, Tailwind
- [x] `globals.css` — full design system CSS vars matching blueprint §47 (--c-bg-primary: #0A0E14, --c-bg-elevated: #121821, all ink/status/border tokens), `pulse-urgent` keyframe animation for S1, mobile safe-area padding, button/input/a base styles
- [x] `layout.tsx` — metadata (title, description, manifest, icon), viewport (themeColor: #0A0E14, no user-scalable)
- [x] `app/page.tsx` — Home: real Firestore `onSnapshot` on `incidents` collection filtered by `venue_id` + ordered by `detected_at desc`; active vs recent split; venue selector dropdown (taj-ahmedabad, house-of-mg, demo-venue); error state; empty state; links to incident detail
- [x] `app/incident/[id]/page.tsx` — Incident detail: 3 real-time Firestore listeners (incident doc + dispatches subcollection + events subcollection); severity-colored emergency background (S1 → #1A0A0A); `SeverityBadge`, `StatusPill`, `CountdownRing` (15s); action buttons (I'M ON IT / Escalate / En route / Arrived) wired to Dispatch service HTTP calls; CASCADE FORECAST section; AGENT TRACE expando showing full event timeline
- [x] `app/drill/page.tsx` — 3-step drill trigger: (1) ingest real JPEG via `POST /v1/frames`, (2) call `POST /v1/analyze` directly (sync path), (3) call `POST /v1/handle-batch`; step-by-step status indicators with color; fallback 67-byte JPEG if `/public/demo-frame.jpg` absent; shows `used_gemini` flag and incident_id in result
- [x] `app/profile/page.tsx` — placeholder with Phase 2 auth note + venue_id display

#### Missing
- [ ] Firebase phone OTP auth — no auth implemented; app runs unauthenticated against Firestore (judges can still see incidents but this is a real gap) (P1)
- [x] `/public/demo-frame.jpg` — real kitchen-fire still image present for the drill trigger
- [x] PWA manifest (`/public/manifest.webmanifest`) — present for both staff and dashboard apps
- [ ] PWA service worker / offline caching — `useOffline` not configured (P1)
- [ ] FCM web push registration — not implemented (P1)
- [ ] Multi-language (en/hi/gu/ta/bn) — not started (P1)
- [ ] WCAG 2.1 AA audit — not done (P1)
- [ ] Emergency mode auto-dismiss when incident moves to RESOLVING

### Dashboard app `apps/dashboard` — **(P0 for Phase 1 demo)**
- [x] **Control-room dashboard exists** — live incident feed, camera mosaic, zone pulse, responder positions, incident detail, and history view implemented; `npm --workspace apps/dashboard run build` passes

### Other apps — all empty
- [ ] `apps/responder` — Flutter app (Phase 2)
- [ ] `apps/authority` — Next.js authority console (Phase 2)
- [ ] `apps/guest-pwa` — Next.js guest PWA (Phase 2)

---

## ─── Shared UI Package `packages/ui-web` ───

### Done
- [x] `src/types.ts` — TypeScript types mirroring Python schemas: `IncidentCategory`, `Severity`, `IncidentStatus`, `DispatchStatus`, `CascadePrediction`, `IncidentClassification`, `Incident`, `Dispatch`, `IncidentEvent`, `SEVERITY_COLOR` record (S1→#DC2626, S2→#EF4444, S3→#F59E0B, S4→#3B82F6), `STATUS_COLOR` record (all 11 statuses)
- [x] `src/firebase.ts` — `getFirebaseApp()`, `getDb()` (Firestore, emulator-aware), `getFirebaseAuth()` (Auth, emulator-aware); reads from `NEXT_PUBLIC_FIREBASE_*` env vars; singleton pattern per module
- [x] `src/components/IncidentCard.tsx` — compact + full variants, `formatElapsed()`, uses `SeverityBadge` + `StatusPill`, design-system colors
- [x] `src/components/SeverityBadge.tsx` — S1/S2/S3/S4 colored pill badges with labels, 3 sizes
- [x] `src/components/StatusPill.tsx` — status dot + label, `STATUS_COLOR` border
- [x] `src/components/CountdownRing.tsx` — SVG ring with 1s interval countdown, `onComplete` callback, configurable size/color, resets on `totalSeconds` change
- [x] `src/index.ts` — barrel export

### Missing (blueprint §50 component library)
- [ ] `AgentTraceView` — shows agent reasoning steps (needed for explainable-AI in dashboard) (P1)
- [ ] `DispatchCard` — actionable card: Accept/Escalate/Decline with responder info (P1)
- [ ] `LiveVideoTile` — CCTV frame with privacy toggle + freeze-frame evidence (P2)
- [ ] `EvacuationRouteStrip` — mini-map of one route (P2)
- [ ] `IntegrityBadge` — audit chain intact/broken indicator (P2)
- [ ] `AuditRow` — row in audit log table (P2)
- [ ] `EmptyState`, `LoadingState`, `ErrorState` — standard three (P1)
- [ ] `ResponderAvatar` — with availability status dot (P1)
- [ ] `ZonePin` — on map overlay (P2)

---

## ─── BigQuery / Audit Infrastructure ───

- [x] `audit.py` — full implementation with BigQuery streaming insert + SHA-256 chain (see shared library section)
- [ ] BigQuery dataset `aegis_audit` with `events` table (DDL from blueprint §25.1) **not created in GCP** — Terraform is empty, no `bq mk` script
- [ ] BigQuery datasets `aegis_analytics` + `aegis_learning` — not created
- [ ] Pub/Sub → BigQuery direct sink subscription — not configured
- [ ] Daily chain integrity verifier Cloud Scheduler job (P2)

---

## ─── Cloud Deployment ─── (P0 for Phase 1 submission)

- [x] Terraform skeleton — `terraform/` now has `versions.tf`, `variables.tf`, `apis.tf`, `pubsub.tf` (all 9 topics + DLQs + pull subs), `bigquery.tf` (audit + analytics + learning datasets, `events` table with partitioning/clustering/schema), `storage.tf` (evidence/reports/assets buckets with lifecycle + retention), `artifact_registry.tf`, `iam.tf` (one SA per service, least-privilege common + service-specific roles), `secrets.tf` (placeholders for SendGrid/MSG91/webhook signing/service secret), `outputs.tf`, plus README and `terraform.tfvars.example`.
- [x] `Dockerfile` for each service — all four present, orchestrator fixed to include `agents/` + `prompts/`, vision + dispatch include `prompts/` too, all use `${PORT:-NNNN}` binding for Cloud Run.
- [x] Deploy script — `scripts/deploy.ps1` rewritten to build via Cloud Build with per-service Dockerfile from the repo root (buildpacks can't resolve sibling `aegis-agents`); sets env vars, min/max instances, CPU/memory, unauthenticated allow, and prints the service URLs at the end.
- [ ] Cloud Run deploy for `ingest`/`vision`/`orchestrator`/`dispatch` to asia-south1 — **scripts ready, but actual `terraform apply` + `deploy.ps1` not executed yet** (codex should run the deploy and paste the URLs)
- [ ] `firebase deploy` (rules + indexes + functions) pushed to production Firestore — not executed yet (`scripts/deploy_firebase.ps1` exists)
- [ ] Public demo URL — blocked on the three deploy steps above
- [x] Pub/Sub topics declared in Terraform: `raw-frames`, `audio-chunks`, `sensor-events`, `perceptual-signals`, `incident-events`, `dispatch-events`, `authority-events`, `audit-events`, `learning-examples` (all with `-dlq` siblings).
- [ ] Pub/Sub push subscriptions pointing at deployed Cloud Run URLs — planned in `terraform/pubsub.tf` as pull subs; promote to push after first deploy by adding the Cloud Run URL to the subscription resource.

---

## ─── CI/CD ───

- [x] `.github/workflows/` — workflows present
- [x] GitHub Actions: lint (ruff + mypy) on PR — configured in `ci.yml`
- [x] GitHub Actions: pytest on PR — configured in `ci.yml` (conditional until more tests land)
- [~] GitHub Actions: Cloud Run deploy on push to main — scaffolded in `deploy.yml`; secrets/canary rollout still need real GCP validation
- [x] `cloudbuild.yaml` — present with Python + web quality steps
- [x] Secrets scanner (gitleaks) in CI — configured in `ci.yml`
- [ ] Container vulnerability scan (Trivy) — not configured

---

## ─── Phase 1 Submission Artifacts ───

- [ ] Demo video (2:30–2:45): hook in first 10s, live end-to-end fire scenario, agent trace visible, dispatch latency shown — **not recorded**
- [ ] 10-slide deck: SDG 3.6/11.5/16.6 (specific targets), agent architecture slide, Phase 2 roadmap slide — **not created**
- [ ] README 5-minute quickstart verified end-to-end — not confirmed
- [ ] License files applied (Apache 2.0 platform, MIT SDK packages, proprietary prompts/fine-tune data) — not done
- [x] `/public/demo-frame.jpg` — real kitchen-fire image present for the drill trigger
- [x] `architecture.md` stale comment — fixed; Gemini path now documented correctly

---

---

# ═══════════════════════════════════════════════
# PHASE 2 — PRODUCT VAULT  (2026-05-30 → 2026-06-09)
# ═══════════════════════════════════════════════

## New services to build (all directories missing)

- [ ] `services/audio/` — Gemini Audio event detection (P1): scream, glass break, fire alarm, smoke alarm, gunshot, crash; consume `audio-chunks` topic; emit `perceptual_signals`
- [ ] `services/fusion/` — Sensor Fusion (P1): spatio-temporal coalescence of vision + audio + IoT signals within ±10s per zone; greedy multi-source dedup; emit fused `perceptual_signals` with unified `fused_signal_id`
- [ ] `services/triage/` — MedGemma wrapper (P1): deploy MedGemma to Vertex AI Endpoint; approved-phrase library at `data/triage_library.json`; ESI 1–5 output; hard output allow-list; "advisory, not medical direction" label on every response; RAG over `medical-kb-v1` Matching Engine index
- [ ] `services/evacuation/` — Flow-aware routing (P1): indoor graph as `networkx` G=(V,E); min-cost max-flow solver; per-guest personalized route cards; Maps Routes API for outdoor legs; staff "corridor blocked" tap triggers re-plan
- [ ] `services/comms/` — Communications (P1): Cloud Translation (5 languages + custom glossary at `/i18n/glossary/`); Cloud TTS neural2 voices; PA API integration (venue-specific webhook); Jinja2 templates with validated placeholders; staff Firestore chat message; authority JSON-LD packet
- [ ] `services/authority/` — Authority dispatcher (P1): Ed25519 signature via Cloud KMS; JSON-LD `schema.org/EmergencyEvent` + Aegis extensions; exponential-backoff retry with email/SMS fallback; MSG91 + SendGrid secrets from Secret Manager
- [ ] `services/analytics/` — BigQuery-backed (P2): views `v_dispatch_latency_by_venue_daily`, `v_false_positive_rate_by_camera_weekly`, `v_incident_volume_by_category_hourly`, `v_responder_sla_by_responder_weekly`; BI Engine cache for sub-second queries
- [ ] `services/venue/` — Onboarding wizard backend (P1): floor plan upload → PNG/SVG → indoor graph generation; zone definition with GeoJSON; staff roster CRUD; responder credentialing + expiry; drill scheduling
- [ ] `services/audit/` — Standalone audit service (P2): chain-verify endpoint for integrity UI; separate from shared lib write path

## New agents to build

- [ ] `agents/triage/agent.py` — See README in that dir for full spec. Key: MedGemma only; output constrained to `data/triage_library.json`; never free-form (P1)
- [ ] `agents/comms/agent.py` — See README. 5 output types; tone rules; no exclamation points (P1)
- [ ] `agents/evacuation/agent.py` — See README. Flow-balanced routing; show bottleneck vs dispersed demo (P1)
- [ ] `agents/post_incident/agent.py` — Sendai-format retrospective; pull from BigQuery audit chain; auto-generated within 48h of resolution (P2)
- [ ] `agents/learning_loop/agent.py` — Batch: resolved incident → structured training example → `aegis_learning.classifier_training_examples` (P2)

## ADK migration
- [ ] Migrate `agents/orchestrator/agent.py` from direct Python async calls to Vertex AI ADK ReAct loop with tool-use protocol; deploy to Vertex AI Agent Engine (P2)
- [ ] Each sub-agent exposed as an ADK `Tool` with strict Pydantic I/O contracts (P2)
- [ ] ADK built-in session checkpointing + Cloud Trace integration (P2)

## Firebase / Auth
- [ ] Cloud Function: `setCustomClaims` — triggered on user creation or role change in Firestore, sets `role` + `venues[]` + `skills[]` custom claims on Firebase Auth token (P1) — **rules reference these claims but nothing sets them**
- [ ] Firebase phone OTP auth in staff app (P1)
- [ ] SAML SSO for authority console (P2)
- [ ] MFA enforcement for corporate admins (P2)
- [ ] Firebase App Check middleware in all services (P1): Play Integrity (Android), App Attest (iOS), reCAPTCHA Enterprise (web)

## Frontend — Phase 2 apps

### `apps/dashboard` (Next.js venue dashboard)
- [x] Sidebar nav: Live / History / Setup / Compliance / Analytics / Billing (P1)
- [x] Live view: active incidents list, camera grid (thumbnail tiles), zone status map, staff positions (P1)
- [x] Incident detail (desktop-rich): full width, video evidence panel, cascade forecast chart, agent trace timeline (P1)
- [~] History: incident log exists, but pagination / advanced filters / CSV export are still missing (P1)
- [ ] Setup sub-screens: venue config, floor plan upload + annotation, zones, cameras, sensors, staff roster, responders (P1)
- [ ] Analytics: 6 sub-dashboards (DL trend, FPR, SAR, TTR, incident volume heatmap, responder SLA) (P2)
- [ ] Compliance: audit trail with integrity indicator, generated reports list, one-click Sendai report export (P2)
- [ ] Drill mode: simulated incident trigger, trace view, no external webhooks (P1)
- [ ] `AgentTraceView` component wired to BigQuery trace data (P1)

### `apps/responder` (Flutter)
- [ ] Availability toggle + active dispatch view (P1)
- [ ] Full-screen incoming dispatch takeover (P1)
- [ ] En route map with incident pin, indoor floor plan (P1)
- [ ] Arrived / handoff flow (P1)
- [ ] Offline-cached indoor map for credentialed venues (P2)

### `apps/authority` (Next.js)
- [ ] SSO login (SAML or email+OTP) (P1)
- [ ] Live feed of incidents from opted-in venues (P1)
- [ ] Incident detail with redacted video evidence (P1)
- [ ] Historical search (P2)
- [ ] Signed evidence bundle export (P2)

### `apps/guest-pwa` (Next.js PWA)
- [ ] QR scan → consent screen → phone verification (P1)
- [ ] Venue status card (nominal / alert / evacuating) (P1)
- [ ] SOS button flow (P1)
- [ ] Evacuation card (activated during incident) (P1)
- [ ] PWA installable + offline-cached evac card (P1)

## Infrastructure
- [ ] Terraform: Pub/Sub topics + push subscriptions + DLQ for all 10 topics (P1)
- [ ] Terraform: Cloud Run services with min-instances, CPU always-on, VPC connector (P1)
- [ ] Terraform: Cloud Storage buckets (evidence CMEK, reports 7yr retention, assets, models) (P1)
- [ ] Terraform: BigQuery datasets + tables with partitioning/clustering DDL (P1)
- [ ] Terraform: IAM bindings per service account (P1)
- [ ] Terraform: Cloud Armor WAF + Cloud LB for web apps (P2)
- [ ] Terraform: Cloud KMS keyring + keys (evidence CMEK, authority signing) (P2)
- [ ] Terraform: Secret Manager secrets (SendGrid, MSG91, PA API creds) (P2)
- [ ] Terraform: Memorystore Redis for Vision dedup cache + Translation cache (P2)
- [ ] Vertex AI Matching Engine indexes: `responders-skills-v1` (dim 512), `medical-kb-v1` (dim 768), `historical-incidents-v1` (dim 768) (P2)
- [ ] Vertex AI Search datastore per venue (SOPs, floor plan text, past post-mortems) (P2)

## Phase 2 features
- [ ] Venue onboarding wizard UI (15-min guided: upload floor plan → annotate zones → map cameras → add staff → test sensors) (P1)
- [ ] MQTT → Pub/Sub bridge for IoT sensor integration (P1)
- [ ] Multi-camera same-event deduplication (Fusion service) (P1)
- [ ] Venue-map-aware spatial signal grouping (P1)
- [ ] Real-time responder ETA + position on map (Google Maps Routes API) (P1)
- [ ] Cascade predictor — improve from heuristic to full Gemini Pro call with venue graph context (P1, partially done — agent exists but needs real venue_graph input)
- [ ] Responder escalation ladder auto-escalate on TIMED_OUT → page backup (P1)
- [ ] Cloud Tasks for durable 15s ack timeout (P1)
- [ ] Multi-lingual guest instructions: Cloud Translation + TTS; 5 languages; custom safety glossary at `/i18n/glossary/` (P1)
- [ ] Staff group chat backed by Firestore `chat_rooms` (P1)
- [ ] Drill mode: all agents run, zero external webhooks fire, full trace visible (P1)
- [ ] Learning loop scaffold: Vertex AI Pipelines, resolved incident → LoRA fine-tune job, weekly cadence (P2)
- [ ] Post-incident Sendai report auto-generation PDF within 48h (P2)
- [ ] Audit integrity verifier UI in dashboard (P2)
- [~] Load test: k6 script scaffold exists in `/tests/load/`, but 50-concurrent-incident validation is still pending (P2)
- [ ] 3 user-interview write-ups in `docs/user-research/` (P2)
- [ ] 1 signed LOI from partner venue (P2)

---

---

# ═══════════════════════════════════════════════
# PHASE 3 — GRAND FINALE  (target: last week June 2026)
# ═══════════════════════════════════════════════

- [ ] Guest-phone sensor fusion (novel §61): on-device wake-word (5 languages), fall detection, scream/glass-break classifier (1s windows); only event labels upload, raw audio/video never leaves phone; Sensor Fusion Service correlates with CCTV + IoT (P2)
- [ ] Crowd-density aware evacuation routing (novel §63): min-cost max-flow over indoor graph, spread egress across exits, real-time re-plan on density spike or staff "corridor blocked" tap, per-guest personalized card updated via FCM (P2)
- [ ] Predictive risk heatmap: BigQuery-backed, which zones trend toward incidents at which times (P2)
- [ ] Fairness dashboard: FPR by demographic camera zone, flag if classifier behaves differently across zones (P2 — novel responsible-AI point for judges)
- [ ] Learning loop accuracy-over-time chart visible in Venue Dashboard (P2)
- [ ] MedGemma dedicated Vertex AI Endpoint deployed (dedicated for HIPAA-like isolation) (P2)
- [ ] VPC Service Controls perimeter on evidence project (P3)
- [ ] Harassment detection sub-classifier (audio cues + behavioral signals) — SDG 5 differentiator (P3)
- [ ] 3-minute final video — shot list per blueprint §91: hook → stats → brand → live demo (timer visible) → novel contributions (cascade, MedGemma, fairness) → traction → CTA (P3)
- [x] Live demo runbook `docs/runbook.md`: exactly what to show, fallback steps if Gemini is slow, screen share setup (P3)
- [ ] Booth banner: 1 image (split-screen CCTV + Aegis at T+12s), 1 number (12 seconds), 1 tagline (Every second is a life) (P3)
- [ ] One-pager leave-behind (P3)
- [ ] 5-min pitch script rehearsed ×3 (blueprint §92) (P3)

---

---

# ═══════════════════════════════════════════════
# CODE QUALITY — FULL AUDIT
# ═══════════════════════════════════════════════

## What's solid
- [x] Pydantic v2 strict models for every wire format
- [x] Structured JSON logging (Cloud Logging compatible field names: severity, message, service, venue_id, incident_id)
- [x] Typed exception hierarchy — every error has http_status + audit_category
- [x] Soft-fail pattern on every external dep — services degrade gracefully without creds
- [x] Tenacity retry with exponential backoff on Gemini calls
- [x] asyncio.Lock for audit hash chain monotonicity under concurrency
- [x] Ordering keys on all Pub/Sub publishes (disabled on emulator, not silently broken)
- [x] Type hints throughout Python (full annotations; `from __future__ import annotations`)
- [x] TypeScript strict mode in ui-web
- [x] ruff config covers security rules (bandit S ruleset), imports, comprehensions, pyupgrade
- [x] mypy strict mode configured

## Critical gaps

### Tests — coverage still far below target
- [~] Unit tests exist for `services/ingest`, `services/vision`, `services/orchestrator`, and `services/dispatch`; `tests/e2e/` and `tests/load/` now have starter scaffolds, but repo-wide coverage is nowhere near the 70% goal
- [~] `services/ingest/tests/` — frame ingest + sensor batch validation covered; max-size rejection still missing
- [~] `services/vision/tests/` — Gemini success/fallback + Pub/Sub subscriber covered; invalid-base64 case still missing
- [~] `services/orchestrator/tests/` — `/v1/handle` and Pub/Sub envelope parsing are covered; deeper dispatch materialization cases still needed
- [~] `services/dispatch/tests/` — happy path + Firestore GET fallback covered; still needs property-based escalation/state-machine coverage
- [~] `tests/agent_evals/` — 7 canonical scenarios (kitchen fire high/med-conf, medical distress, crowd surge, false-positive steam, nominal lobby, multi-signal fire+sensor) + `scenarios.json` so new scenarios drop in as data. 9 tests in `test_classifier_eval.py` covering the rule-based classifier contract, Gemini-fallback behaviour, and dispatcher hard-filter/skill-match. **Pass on every run; blueprint §82 regression gate now exists.** Next: grow to 50 scenarios and add golden-file check for live Gemini outputs.
- [ ] `agents/cascade/tests/` — heuristic fallback per category not yet covered (the orchestrator eval exercises it indirectly via the dispatcher test)
- [x] `packages/ui-web/src/__tests__/` — vitest + jsdom + @testing-library/react suite: 7 tests covering `SeverityBadge` (label + color per severity), `StatusPill` (status token + border color), `CountdownRing` (initial render, 1-second decrement, `onComplete` fires at zero, reset on totalSeconds change). `npm --workspace packages/ui-web run test` green.

### CI — nothing running
- [x] `.github/workflows/ci.yml` — on PR: ruff check + format check + mypy + pytest (conditional until more tests exist) + ESLint
- [~] `.github/workflows/deploy.yml` — on push to main: deploy scaffold added, but changed-service detection / Artifact Registry / canary rollout still need real implementation
- [x] `.pre-commit-config.yaml` — local enforcement scaffold for ruff, mypy, gitleaks, eslint, prettier

### Stale documentation
- [x] `docs/architecture.md` line: "The Vision classifier is a deterministic stub" — fixed
- [x] `docs/decisions/` — ADRs added for: Vision real Gemini vs stub decision, Next.js pivot from Flutter, dispatcher ranking approach, cascade Gemini Pro fallback strategy

### Additional quality issues
- [~] `services/dispatch/main.py` in-memory `memory_store` dict — GET now hydrates from Firestore, but transitions/timeouts still need durable backing for multi-instance safety.
- [x] Vision service has `POST /pubsub/raw-frames` endpoint — fully event-driven pipeline path now exists and is test-covered.
- [x] Classifier / Cascade / Dispatcher-rerank prompts extracted to `/prompts/*.md`, loaded via `PromptRegistry`, `prompt_hash` logged on every Gemini call for audit trail.
- [ ] `apps/staff/src/app/profile/page.tsx` is a placeholder with hardcoded Phase 2 note — fine for demo but document as known stub
- [x] Drill page real still image is present at `/apps/staff/public/demo-frame.jpg` (fallback remains only as backup)

---

---

# ═══════════════════════════════════════════════
# SECURITY & PRIVACY — FULL AUDIT (blueprint §61–70)
# ═══════════════════════════════════════════════

- [x] Firestore security rules — venue membership, role claims, dispatch update restricted to assigned responder, default-deny catch-all
- [x] Firebase Admin SDK used for backend writes (bypasses client rules correctly)
- [x] `SafetyEnvelopeViolation` exception defined and raised appropriately in agents
- [x] Firebase App Check + ID-token verification primitive — `aegis_shared.auth.verify_request` is a FastAPI dependency that decodes `Authorization: Bearer <idToken>` + `X-Firebase-AppCheck: <token>`, returns a typed `Principal`, enforces or bypasses based on `AEGIS_ENV` / `AEGIS_REQUIRE_AUTH` / `FIREBASE_APP_CHECK_REQUIRED`. Each service needs one line (`principal: Principal = Depends(verify_request)`) to mount it.
- [x] Custom claims Cloud Function scaffolded at `firebase/functions/src/index.js` — Firestore trigger on `/users/{uid}` translates the user doc's `role` / `venues` / `skills` into Firebase Auth custom claims so `request.auth.token.role` in rules becomes real. `firebase.json` updated with a `functions` block pointing at this source.
- [ ] Cloud DLP redaction on frames — **not implemented anywhere**. Every frame goes to Gemini unredacted. (P1)
- [ ] mTLS between Edge Gateway and Ingest — not configured (P2)
- [ ] Cloud KMS CMEK on evidence bucket — not configured (Terraform empty) (P2)
- [ ] Secret Manager bindings for SendGrid, MSG91, PA API creds — not configured (P2)
- [ ] VPC Service Controls perimeter on evidence project — P3
- [ ] Consent management UI — not built (P2)
- [ ] Right-to-be-forgotten cascade delete — not built (P2)
- [ ] Security Command Center Standard tier — not confirmed enabled (P2)
- [ ] HRACC / NDMA compliance report PDF export — not built (P2)
- [ ] Dependency vulnerability scan (pip-audit / safety) — not in CI (P1)
- [ ] WCAG 2.1 AA audit on all web surfaces — not done (P1)
- [ ] Drill mode isolation: safeguard against firing real 108/fire webhooks during drill — **not implemented in orchestrator** (P1)

---

---

# ═══════════════════════════════════════════════
# OBSERVABILITY — FULL AUDIT (blueprint §22)
# ═══════════════════════════════════════════════

- [x] Structured Cloud Logging in all Python services (structlog JSON, Cloud Logging field names)
- [x] Local audit JSONL at `.audit/aegis_audit.jsonl` — human-readable during dev
- [x] BigQuery audit streaming insert wired (soft-fail in dev)
- [ ] Cloud Monitoring dashboards — `monitoring/dashboards/` is **empty**. No dashboard JSON.
- [ ] Cloud Monitoring alert policies — `monitoring/alerts/` is **empty**. No alert configs.
- [ ] OTEL distributed tracing — referenced in architecture.md but zero instrumentation code in any service. No `opentelemetry` imports.
- [ ] Custom metrics for Dispatch Latency (p95), FPR, SAR emitted to Cloud Monitoring — not implemented
- [ ] SLO definitions (99.5% orchestrator availability) — not configured
- [ ] Cloud Profiler env var on Cloud Run — not in service configs
- [ ] Error Reporting structured error format — not confirmed (structlog format may not match Cloud Error Reporting's expected shape)
- [ ] Firebase Crashlytics — no Flutter apps built yet
- [ ] Firebase Performance Monitoring — no Flutter apps built yet
- [ ] Synthetic monitors (every-5-min ping of full pipeline) — not configured
- [ ] Cloud Trace propagation via Pub/Sub message attributes — not implemented
- [ ] Dispatch Latency logged as a structured field on `incident.dispatched` audit event — not confirmed; only `explanation` string logged

---

---

# ═══════════════════════════════════════════════
# IMMEDIATE BLOCKERS — PHASE 1 SUBMISSION
# ═══════════════════════════════════════════════

These 8 items block a submittable Phase 1. Do these first, in order:

1. [x] **Build `apps/dashboard`** — live control-room dashboard now exists, includes Firestore incident feed, and passes production build.

2. [~] **Deploy to Cloud Run** — everything the deploy needs is now in the repo: Terraform full skeleton (`terraform/*.tf`), fixed Dockerfiles (orchestrator copies `agents/` + `prompts/`; vision/dispatch copy `prompts/`), rewritten `scripts/deploy.ps1` that builds via Cloud Build + deploys with explicit env vars. Remaining: run `terraform apply` then `scripts/deploy.ps1` and capture the URLs.

3. **`firebase deploy`** — push `firestore.rules` + `firestore.indexes.json` + `firebase/functions/syncCustomClaims`. Without this, the staff app will hit permission errors on a real Firebase project. `firebase.json` is now configured for Node 20 functions.

4. [x] **Add real demo frame** — kitchen-fire JPEG is present in `apps/staff/public/demo-frame.jpg` (and mirrored in dashboard public assets).

5. [x] **Fix `architecture.md`** — stale stub wording removed and real Gemini behavior documented.

6. [x] **Fix `smoke.ps1` Vision expectation** — script now validates a structured vision response instead of forcing `category_hint == "FIRE"`.

7. **Record demo video** — 2:30–2:45. Use the drill page end-to-end. Show the timer, show the agent trace, show the dispatch on the staff app. This is what judges score first.

8. **Build the 10-slide deck** — required for Phase 1 scoring. Include: hook (India incident stats), problem, solution one-liner, agent architecture diagram, SDG 3.6/11.5/16.6 (specific target numbers), Phase 1 demo screenshot, Phase 2 roadmap, team slide.

---

## New since last progress audit (2026-04-24 session 2)

Context for whoever reads next:

- **Prompts** — Classifier, Cascade Predictor, and Dispatcher Re-rank prompts extracted from inline Python strings into `/prompts/classifier.md`, `/prompts/cascade_predictor.md`, `/prompts/dispatcher_rerank.md`. Agents load them via `aegis_shared.prompts.load_prompt(name)`. `prompt_hash` is logged on every Gemini call and belongs on every audit row.
- **Drill mode + safety envelope** — `OrchestratorAgent.run` reads `venue_context.drill_mode` and `venue_context.autonomous_mode`, stamps a `incident.drill_mode_enabled` audit event, tags every `dispatch-events` payload with `drill=true`, and gates S1 auto-dispatch on autonomous opt-in. Drill flag is merged from `HandleBatchRequest.drill_mode` convenience field.
- **Auth primitive** — `aegis_shared.auth.Principal` + `verify_request` FastAPI dependency + `require_role(*roles)` factory. Verifies Firebase ID token, verifies App Check token when present, reuses `firebase_admin` app singleton from `aegis_shared.fcm`. Bypasses in local/dev unless `AEGIS_REQUIRE_AUTH=1`.
- **Custom claims Cloud Function** — `firebase/functions/src/index.js` with `syncCustomClaims` Firestore trigger on `/users/{uid}`; `firebase.json` updated to declare the functions source (nodejs20). This is what makes every `request.auth.token.role` / `venues` check in `firestore.rules` resolve to real values.
- **Terraform** — 9 topics + DLQs + pull subs, audit/analytics/learning BQ datasets with the `events` table from blueprint §25.1, three buckets with lifecycle + retention, Artifact Registry repo, one service account per Cloud Run service with least-privilege IAM, Secret Manager placeholders, outputs. Root module, GCS backend, variables + example tfvars.
- **Dockerfiles** — Orchestrator now copies `agents/`, installs it, then installs the service with `--no-deps` + explicit deps (plain pip can't resolve uv path sources). All services also copy `/prompts/` so `PromptRegistry` resolves in the container.
- **Deploy script** — `scripts/deploy.ps1` rewritten to build via Cloud Build from the repo root with per-service Dockerfile, then deploy with explicit env vars and Cloud Run config. Buildpack mode (`--source .` per service dir) would fail because sibling paths aren't resolvable.
- **Agent eval harness** — `tests/agent_evals/scenarios.json` (7 scenarios) + `test_classifier_eval.py` (9 tests: scenario parametric, Gemini fallback, dispatcher skill-match). All pass. Blueprint §82 regression gate now exists; grow to 50 scenarios in Phase 2.
- **UI component tests** — vitest + jsdom + @testing-library/react in `packages/ui-web`. 7 tests: `SeverityBadge` (×2), `StatusPill` (×2), `CountdownRing` (×3 incl. async fake-timer tick of a 3-second countdown to zero and reset-on-prop-change). `npm --workspace packages/ui-web run test` green.

Python test suite is **32 tests passing**, UI suite is **7 tests passing**, agent-eval suite is **9 tests passing**. Staff PWA builds clean (`npm --workspace apps/staff run build` ✓).

What still blocks a live Phase 1 URL: executing `terraform apply`, `scripts/deploy.ps1`, `scripts/deploy_firebase.ps1`, and adding the deployed Cloud Run URLs to the `push_config.push_endpoint` of the Pub/Sub subscriptions that were declared as pull-first.

---

## New since last audit (2026-04-25 — deploy-day updates)

**Deploy target pivoted to Firebase App Hosting (not static Firebase Hosting).** App Hosting runs Next.js as a managed Cloud Run service inside the same project — full SSR, live Firestore listeners on the server, auto TLS, GitHub auto-deploy. DEPLOY.md rewritten end-to-end to match.

- [x] `firebase.json` now declares two App Hosting backends (`aegis-staff`, `aegis-dashboard`) pointing at `apps/staff/` and `apps/dashboard/` root dirs, each with its own `apphosting.yaml` for runtime config.
- [x] Root-level `apphosting.yaml` is a fallback build config; each app's per-backend `apphosting.yaml` is where you set `minInstances`, env vars, secrets.
- [x] Root `package.json` simplified: no more npm workspaces (App Hosting's build environment couldn't resolve sibling path deps from inside `apps/staff/`). Just convenience scripts that `cd` into each app.
- [x] Shared React package `@aegis/ui-web` now ships to each app as a packed tarball: `packages/ui-web` builds via `tsc -p tsconfig.json` (tsconfig updated with `noEmit: false`, `outDir: "dist"`), `npm pack` produces `aegis-ui-web-0.1.0.tgz`, and both apps reference it as `file:aegis-ui-web-0.1.0.tgz`. CI re-packs on every run so a stale tgz can't slip through.
- [x] `scripts/pack-ui.ps1` + `scripts/pack-ui.sh` automate the build → pack → copy-to-both-apps workflow. Run after every change under `packages/ui-web/`, commit the new `.tgz` in both app dirs.
- [x] `.github/workflows/ci.yml` rewritten — the previous file got its indentation destroyed during an edit and failed to parse. New version matches the non-workspaces layout: pack ui-web → `cd apps/<app> && npm install && npm run lint && npm run build`, Python quality job unchanged, Terraform validate job added.
- [x] `services/shared/aegis_shared/firestore.py::get_dispatch_by_id` switched from deprecated positional `.where("x", "==", y)` to the `FieldFilter` kwarg form. Eliminates the UserWarning that would become a hard error in a future Firestore SDK release.
- [x] `requirements.txt` Windows absolute paths replaced with relative editable installs (`-e ./services/shared`, `-e ./agents`, etc.) so CI can install on Ubuntu.

Deploy status: staff + dashboard shipped to App Hosting, Cloud Run backend services scripts ready but not run yet. Firebase Functions + Firestore rules not pushed yet.

Known remaining gaps (deliberate — Phase 2): see Appendix C of DEPLOY.md.

---

---

# ═══════════════════════════════════════════════
# HOW TO UPDATE THIS FILE
# ═══════════════════════════════════════════════

- Finish a task → `[ ]` → `[x]`. Add one-line note if non-obvious (e.g., "switched to Cloud Tasks for durable timeout").
- Partially done → `[~]` with a "what is left" comment inline.
- New gap discovered → add under the relevant section with `[ ]`.
- Never mark `[x]` unless you have personally verified the code runs end-to-end.
- After any major new build, re-read the corresponding blueprint section (§7 features, §11 architecture, §82 testing) to catch newly applicable items.
