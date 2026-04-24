# ADR-0001: Core technology stack for Aegis

**Status:** Accepted · 2026-04-23 · Proposer: @ubaid

## Context

Aegis is a four-person, nine-week build (Phase 1 → Grand Finale) that has
to (a) cleanly integrate many Google products to clear the Solution
Challenge "Technical Merit" 40% weight bar, (b) feel responsive in a live
demo, and (c) survive a real Grand Finale pitch with Google engineers
asking detailed architecture questions.

Possible stacks considered:

1. **GKE + microservices + Kafka + Postgres + Angular + React Native**
2. **Cloud Run + Pub/Sub + Firestore + Next.js + Flutter** ← chosen
3. **App Engine monolith + Firebase + Flutter**
4. **Single Python monolith + Firebase Auth + Flutter**

## Decision

We pick option 2 for the following reasons.

### Why Cloud Run over GKE

We don't have a dedicated DevOps engineer. Cloud Run gives us
auto-scaling, HTTPS, per-request billing, zero-ops, and up to 60 minutes
of request timeout out of the box. GKE would soak 20–30% of our build
time in cluster operations with zero visible output to judges. If we
outgrow Cloud Run later — latency SLO requires persistent instances, or
we need custom networking — we migrate then.

### Why Pub/Sub over Kafka or direct HTTP

Incident flow is inherently event-driven (signal → classify → dispatch).
Pub/Sub gives us backpressure, ordering keys per venue, DLQ, and replay
for testing with zero cluster management. Kafka is strictly more
powerful and strictly the wrong choice for a 4-person team in 9 weeks.
Direct HTTP between services would couple them tightly and make Phase 2
agent fan-out messy.

### Why Firestore over Postgres

Every client surface needs real-time state (active incidents, staff
positions, dispatch status). Firestore gives us WebSocket-feel UI
updates for free via `onSnapshot`. Postgres would require us to build
and operate our own WebSocket layer. Firestore's tradeoffs — limited
query expressiveness, document size ceiling — are acceptable for our
data shape (most documents are per-incident subdocuments, not huge
aggregates). BigQuery handles the analytics side.

### Why Next.js + Flutter, not React Native for mobile

Flutter on Android is significantly better than React Native on the
₹8,000 phone class our staff persona actually uses. Flutter's widget
model also gives us a single codebase for Android + iOS + Web (for the
guest PWA we can reuse components later if desired). Next.js on the web
side is the fastest path to a production-grade dashboard with
server-side rendering, API routes, and Firebase SDK integration.

### Why Vertex AI ADK for agents

The 2026 theme is "Build with AI" and ADK is Google's current flagship
agent framework. Judges from the Vertex AI team will grade us against
this specifically. An in-house agent loop using raw Gemini calls would
score lower on Technical Merit even if functionally equivalent. ADK
also gives us built-in tracing (Cloud Trace compatible) which is gold
in a live demo.

## Consequences

### Positive

- Every service deploys with one `gcloud run deploy` command
- Firestore real-time listeners eliminate a whole category of
  WebSocket plumbing work
- Pub/Sub scales to hackathon-demo load and Year-1 production load
  with no changes
- Agent tracing is free — we can show a live trace to Grand Finale
  judges, which is the single best visual signal of "this is a real
  AI system, not a Gemini wrapper"

### Negative / Accepted tradeoffs

- Cold starts on Cloud Run add ~200–500ms p99 to low-traffic services.
  Mitigation: `min_instances=1` on the hot path (Orchestrator,
  Dispatch, Vision). This costs ~$15/month per service, well within
  our credit budget.
- Firestore is weaker than SQL for complex joins. Mitigation: BigQuery
  holds the analytical data; Firestore holds only live state.
- Pub/Sub ordering keys cap throughput per key at 1 MB/s. Mitigation:
  ordering keys are per-incident, and a single incident never
  approaches that throughput.
- ADK is relatively new; there will be rough edges. Mitigation: we
  have a deterministic Phase 1 fallback (already shipped in
  `services/orchestrator/main.py`) that runs without ADK, so the demo
  never depends on ADK being flawless.

### Review trigger

Re-open this ADR if any of the following occur:

- p95 Dispatch Latency exceeds 3s due to Cloud Run cold starts
- Firestore listener count per venue exceeds 1,000 concurrent (billing
  impact)
- ADK hits a hard limitation we cannot work around in ≤2 days
- We sign an enterprise customer who mandates VPC Service Controls
  requiring architectural changes
