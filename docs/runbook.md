# Aegis Demo Runbook

This runbook is the operating guide for the current Phase 1 vertical slice.
It is optimized for live demos, local smoke tests, and quick recovery if one
part of the stack fails.

---

## 1. What is in scope right now

Current critical path:

1. `services/ingest` accepts a frame or sensor signal.
2. `services/vision` analyzes a frame with Gemini or a local fallback.
3. `services/orchestrator` classifies the incident and emits dispatch events.
4. `services/dispatch` pages responders and tracks state transitions.
5. `apps/staff` shows the mobile responder flow.
6. `apps/dashboard` shows the desktop control-room view.

Supported demo mode:

- Local emulators for Firestore and Pub/Sub
- Real Gemini path when credentials are available
- Fallback heuristic path when Gemini is unavailable
- Demo still image at `apps/staff/public/demo-frame.jpg` and `apps/dashboard/public/demo-frame.jpg`

---

## 2. Pre-demo checklist

Run these before any judge session:

1. Confirm `.env` exists and contains Firebase + Gemini credentials or emulator endpoints.
2. Start Docker services: Firestore emulator, Pub/Sub emulator, Redis.
3. Start the four FastAPI services with `scripts/dev.ps1` or `scripts/dev.sh`.
4. Start the web apps:
   - `npm --workspace apps/staff run dev`
   - `npm --workspace apps/dashboard run dev`
5. Run `scripts/smoke.ps1` or `scripts/smoke.sh`.
6. Open:
   - Staff app: `http://localhost:3001`
   - Dashboard app: `http://localhost:3002`
   - Service docs: `:8001/docs`, `:8002/docs`, `:8003/docs`, `:8004/docs`

If any step fails, do not start the demo until the smoke script is green.

---

## 3. Local startup sequence

### Option A — one-command service startup

Use:

```powershell
.\scripts\dev.ps1
```

This loads `.env` and opens a dedicated PowerShell window for each core
service.

### Option B — manual startup

Use separate terminals:

```powershell
cd services\ingest
..\..\ .venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Repeat for:

- `vision` on `8002`
- `orchestrator` on `8003`
- `dispatch` on `8004`

---

## 4. Judge demo flow

Recommended live story:

1. Start on the dashboard home page.
2. Show the empty or nominal venue state.
3. Open `/drill` in the dashboard or staff app.
4. Trigger the drill.
5. Show the three-step flow:
   - frame accepted by Ingest
   - Vision classifies the frame
   - Orchestrator creates an incident and dispatch
6. Return to the dashboard live board.
7. Open the live incident detail page.
8. Show:
   - evidence panel
   - cascade forecast
   - responder ladder
   - trace timeline
9. Open the staff app and acknowledge the dispatch.
10. Move the dispatch through `ack → enroute → arrived`.

If judges are short on time, prioritize:

1. Trigger drill
2. Dashboard incident detail
3. Staff acknowledgement

---

## 5. Operational URLs

### Web surfaces

- Staff app: `http://localhost:3001`
- Dashboard app: `http://localhost:3002`

### Service health endpoints

- Ingest: `http://localhost:8001/health`
- Vision: `http://localhost:8002/health`
- Orchestrator: `http://localhost:8003/health`
- Dispatch: `http://localhost:8004/health`

### Key API endpoints

- Ingest frame: `POST /v1/frames`
- Vision analyze: `POST /v1/analyze`
- Orchestrator handle: `POST /v1/handle`
- Orchestrator batch handle: `POST /v1/handle-batch`
- Dispatch ack: `POST /v1/dispatches/{id}/ack`

---

## 6. Failure modes and fallback plan

### Gemini is unavailable or slow

Symptoms:

- Vision classify call takes too long
- `used_gemini = false`
- Category comes back as low-confidence fallback

Fallback:

1. Continue the demo.
2. Call out that the service degraded gracefully instead of failing closed.
3. Use the dashboard trace and dispatch flow to show the event backbone still works.

### Firestore is unavailable

Symptoms:

- Dashboard or staff app stops updating
- Service logs warn about Firestore soft-fail behavior

Fallback:

1. Use direct API responses from `/v1/analyze` and `/v1/handle-batch`.
2. Show the service docs and JSON response as proof of end-to-end reasoning.
3. Restart emulators if required.

### Dispatch state did not update

Symptoms:

- A button click on the incident detail page does nothing
- `GET /v1/dispatches/{id}` shows an old status

Fallback:

1. Retry the button once.
2. Hit the dispatch endpoint directly in the browser or Postman.
3. If needed, retrigger a fresh drill and walk through the new dispatch ID.

### Web UI is broken but services are healthy

Fallback:

1. Use `scripts/smoke.ps1`.
2. Show service docs and live JSON responses.
3. Explain that the event pipeline still works and UI polish is an active build item.

---

## 7. Quick recovery actions

When the stack drifts during a live session:

1. Close stray service terminals.
2. Restart emulators.
3. Run `scripts/dev.ps1`.
4. Run `scripts/smoke.ps1`.
5. Reload dashboard and staff pages.

If only the web layer is stale:

1. Stop the Next.js process.
2. Restart the relevant app with `npm --workspace <app> run dev`.
3. Hard refresh the browser.

---

## 8. Deployment notes

Current repo helpers:

- `scripts/deploy.ps1` deploys the four core services to Cloud Run.
- `scripts/deploy_firebase.ps1` pushes Firestore rules and indexes.

Recommended deployment order:

1. Deploy Firebase rules and indexes.
2. Deploy Ingest.
3. Deploy Vision.
4. Deploy Orchestrator.
5. Deploy Dispatch.
6. Verify service health endpoints.
7. Update web app env vars to point at the deployed services.

---

## 9. After-action checklist

After any real demo or drill:

1. Save screenshots of the dashboard and staff acknowledgment state.
2. Record whether Gemini or fallback handled the incident.
3. Note any latency spikes or manual workarounds used.
4. Update `progress.md` if a blocker was fixed or a new gap appeared.
5. Capture one thing to improve before the next demo.
