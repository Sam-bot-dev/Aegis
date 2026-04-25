# Aegis — Deployment Guide
### Phase 1 production deploy · last updated 2026-04-25

> **Prereq:** `SETUP.md` is completed end-to-end. This document picks up from a
> green local environment and walks you through everything needed to stand Aegis
> up on real infrastructure, in the right order, with verification checks after
> each step.

---

## Platform recommendation (what we actually shipped on)

| Surface | Where | Why |
|---|---|---|
| **Python services** (ingest / vision / orchestrator / dispatch) | **Cloud Run** (asia-south1) | Blueprint §16.1 — per-request billing, auto-scale, CPU-always on hot path, tight Pub/Sub / Firestore / Vertex AI integration. Region matters: asia-south1 is closest to Indian venues. |
| **Next.js web apps** (staff PWA, venue dashboard) | **Firebase App Hosting** (managed Next.js on Cloud Run under the hood) | Full server-side Next.js — no static-export friction, server components, live Firestore listeners on the server, auto TLS, GitHub auto-deploy, per-commit preview channels. Same project as Firestore / Auth / FCM — zero cross-cloud hops. |
| **Firestore + Auth + FCM + Cloud Functions** | **Firebase** (same GCP project) | Already created in `SETUP.md`. |
| **Pub/Sub, BigQuery, Cloud Storage, Artifact Registry, Secret Manager** | **GCP** (Terraform) | One `terraform apply` creates all of them. |

**Why not Vercel / Render for the web apps?** Cross-cloud hops to Firestore,
Firebase Auth, FCM add 30–60 ms to every call and require custom CORS / App
Check plumbing. App Hosting runs the Next.js app in Cloud Run inside the same
project, so Firestore calls stay intra-region.

**Why not Firebase Hosting (static) for the web apps?** Our apps use live
Firestore subscriptions plus per-request config — static export requires
pre-baking everything at build time. App Hosting gives real SSR with zero
Cloud Run ops.

**Do NOT deploy backend to Vercel or Render.** Stateful (Pub/Sub push
subscriptions, Firestore listeners, FCM Admin SDK), needs Google-issued
service account credentials for Gemini / BigQuery / DLP, event-driven
architecture needs a stable HTTPS URL — exactly Cloud Run's sweet spot.

---

## Layout recap — what files control the deploy

```
repo/
├─ firebase.json               # declares the TWO App Hosting backends
├─ apphosting.yaml             # root-level fallback build config
├─ apps/staff/
│   ├─ apphosting.yaml         # per-backend run config (minInstances, env)
│   └─ aegis-ui-web-0.1.0.tgz  # packed local dep — regenerate with pack-ui
├─ apps/dashboard/
│   ├─ apphosting.yaml
│   └─ aegis-ui-web-0.1.0.tgz
├─ packages/ui-web/            # shared React components (source of the tgz)
├─ scripts/
│   ├─ pack-ui.ps1 / pack-ui.sh   # rebuild + distribute the ui-web tgz
│   ├─ deploy.ps1                 # Cloud Run deploy for the 4 Python services
│   └─ deploy_firebase.ps1        # firebase deploy rules/indexes/functions
└─ terraform/                  # all of GCP
```

**The critical gotcha that broke our first deploy attempt:** the web apps
depend on `@aegis/ui-web` via a packed `.tgz`, not via npm workspaces. Every
time you change `packages/ui-web/`, re-run `pack-ui` before rebuilding or
redeploying the apps. CI re-packs on every run, so a stale tgz blocks merge,
but you still need it to be right locally before pushing.

---

## 0 · One-time prep (15 min)

```powershell
gcloud --version                # ≥ 510
firebase --version              # ≥ 13.x — supports apphosting
docker --version
terraform --version 2>$null     # winget install HashiCorp.Terraform
gcloud config get-value project # aegis-gsc-2026 (or yours)
gcloud auth list
gcloud auth application-default print-access-token > $null
```

**Sanity check — local still green:**

```powershell
# From repo root
python -m ruff check .
python -m ruff format --check services agents tests
python -m mypy services agents
pytest -q
.\scripts\pack-ui.ps1
cd apps/staff; npm install; npm run build; cd ../..
cd apps/dashboard; npm install; npm run build; cd ../..
```

If anything fails, **do not proceed**. Fix locally first.

---

## 1 · Provision infrastructure (Terraform)

Creates Pub/Sub topics + DLQs + pull subs, BigQuery datasets + audit table,
Cloud Storage buckets, Artifact Registry repo, per-service service accounts
with least-privilege IAM, Secret Manager placeholders.

```powershell
cd terraform

# One-time: create the remote-state bucket (replace <your-name>).
gcloud storage buckets create gs://aegis-tf-state-<your-name> `
  --location=asia-south1 --uniform-bucket-level-access

Copy-Item terraform.tfvars.example terraform.tfvars
notepad terraform.tfvars    # set project_id, region, env

terraform init -backend-config="bucket=aegis-tf-state-<your-name>"
terraform plan -out=tfplan
terraform apply tfplan
terraform output
```

**Verification:**

```powershell
gcloud pubsub topics list --filter="name~aegis" | findstr /c:"raw-frames"
bq ls aegis_audit
gcloud storage buckets list --filter="name~aegis"
gcloud artifacts repositories list --location=asia-south1
gcloud iam service-accounts list --filter="email~aegis-"
```

---

## 2 · Populate Secret Manager

```powershell
$s = [Convert]::ToBase64String((1..48 | ForEach-Object {Get-Random -Max 256}))
$s | gcloud secrets versions add service-internal-secret --data-file=-

openssl genpkey -algorithm ed25519 -out /tmp/aegis-webhook.pem
Get-Content /tmp/aegis-webhook.pem | `
  gcloud secrets versions add authority-webhook-signing-key --data-file=-

"placeholder" | gcloud secrets versions add sendgrid-api-key --data-file=-
"placeholder" | gcloud secrets versions add msg91-auth-key --data-file=-
```

---

## 3 · Build + deploy Cloud Run (Python) services

```powershell
.\scripts\deploy.ps1
```

The script, for each of ingest / vision / orchestrator / dispatch:

1. Builds the Docker image via **Cloud Build** with the repo root as the
   build context (buildpacks can't resolve the sibling `aegis-agents` path).
2. Pushes to Artifact Registry.
3. Deploys to Cloud Run, attaching the Terraform-created service account,
   with `--set-env-vars AEGIS_ENV=prod,GCP_PROJECT_ID=…`.

**Verification:**

```powershell
$urls = gcloud run services list --region=asia-south1 --format="value(metadata.name,status.url)"
foreach ($line in $urls) {
  $parts = $line -split "`t"
  Invoke-WebRequest "$($parts[1])/health" -UseBasicParsing | Select StatusCode,Content
}
```

Every service returns `200 {"status":"ok","service":"<name>"}`.

---

## 4 · Promote pull subscriptions to push

```powershell
$PROJECT = gcloud config get-value project
$URL_VISION = gcloud run services describe aegis-vision       --region=asia-south1 --format="value(status.url)"
$URL_ORCH   = gcloud run services describe aegis-orchestrator --region=asia-south1 --format="value(status.url)"
$URL_DSP    = gcloud run services describe aegis-dispatch     --region=asia-south1 --format="value(status.url)"

gcloud pubsub subscriptions modify-push-config raw-frames-pull `
  --push-endpoint="$URL_VISION/pubsub/raw-frames"

gcloud pubsub subscriptions modify-push-config perceptual-signals-pull `
  --push-endpoint="$URL_ORCH/pubsub/perceptual-signals"

gcloud pubsub subscriptions modify-push-config dispatch-events-pull `
  --push-endpoint="$URL_DSP/pubsub/dispatch-events"
```

---

## 5 · Seed the demo venue

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = ".\.secrets\service-account.json"
python scripts/seed_venue.py config/venues/taj-ahmedabad.json --prod
```

Writes the blueprint §24.1 venue doc + zones + cameras + sensors + responders.

---

## 6 · Firebase rules, indexes, and Cloud Functions

```powershell
.\scripts\deploy_firebase.ps1
# or:
firebase deploy --only firestore:rules,firestore:indexes,functions
```

---

## 7 · Firebase App Hosting — deploy staff + dashboard

**`firebase.json`** declares two backends:

```json
{
  "apphosting": [
    { "backendId": "aegis-staff",     "rootDir": "apps/staff",     "alwaysDeployFromSource": true },
    { "backendId": "aegis-dashboard", "rootDir": "apps/dashboard", "alwaysDeployFromSource": true }
  ]
}
```

Each app has an `apphosting.yaml` at its `rootDir` controlling runtime.

### 7.1 First-time backend creation (interactive, once)

```powershell
firebase apphosting:backends:create --project=$PROJECT
# Backend ID:       aegis-staff
# Root directory:   apps/staff
# GitHub repo:      <org>/<repo>
# Branch:           main

firebase apphosting:backends:create --project=$PROJECT
# Backend ID:       aegis-dashboard
# Root directory:   apps/dashboard
# Branch:           main
```

After creation, App Hosting returns two URLs like:

```
https://aegis-staff--<proj>.us-central1.hosted.app
https://aegis-dashboard--<proj>.us-central1.hosted.app
```

These are the **public Phase 1 demo URLs**.

### 7.2 Regenerate the packed @aegis/ui-web tgz

Whenever `packages/ui-web/` changes, re-pack before commit:

```powershell
.\scripts\pack-ui.ps1
git add apps/staff/aegis-ui-web-0.1.0.tgz apps/dashboard/aegis-ui-web-0.1.0.tgz
git commit -m "chore: repack @aegis/ui-web"
```

### 7.3 Per-backend environment variables

Set via `firebase apphosting:config:set` OR via `apps/<app>/apphosting.yaml`:

```powershell
firebase apphosting:config:set `
  --backend aegis-staff `
  NEXT_PUBLIC_FIREBASE_PROJECT_ID=$PROJECT `
  NEXT_PUBLIC_FIREBASE_API_KEY=<web-api-key> `
  NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=$PROJECT.firebaseapp.com `
  NEXT_PUBLIC_FIREBASE_APP_ID=<app-id> `
  NEXT_PUBLIC_INGEST_URL=$URL_INGEST `
  NEXT_PUBLIC_VISION_URL=$URL_VISION `
  NEXT_PUBLIC_ORCHESTRATOR_URL=$URL_ORCH `
  NEXT_PUBLIC_DISPATCH_URL=$URL_DSP `
  NEXT_PUBLIC_DEMO_VENUE_ID=taj-ahmedabad

# Repeat for aegis-dashboard.
```

Or in `apps/staff/apphosting.yaml`:

```yaml
runConfig:
  minInstances: 0
env:
  - variable: NEXT_PUBLIC_FIREBASE_PROJECT_ID
    value: aegis-gsc-2026
    availability: [BUILD, RUNTIME]
  - variable: NEXT_PUBLIC_VISION_URL
    value: https://aegis-vision-xxx.a.run.app
    availability: [BUILD, RUNTIME]
  # ...
```

### 7.4 Push to main → automatic deploy

Each backend is attached to `main`. Every push that touches the backend's
`rootDir` triggers a rollout. Watch it:

```powershell
firebase apphosting:rollouts:list --backend aegis-staff
firebase apphosting:rollouts:get <rollout-id> --backend aegis-staff
```

Force a rollout without waiting for git:

```powershell
firebase deploy --only apphosting:aegis-staff,apphosting:aegis-dashboard
```

### 7.5 Common App Hosting build failures (what we actually hit)

| Symptom | Cause | Fix |
|---|---|---|
| Build fails with `Cannot find module '@aegis/ui-web'` | Stale or missing tgz in the app directory | Run `.\scripts\pack-ui.ps1`, commit, push. |
| Build succeeds but UI renders blank | ui-web tgz built from stale `dist/` — needs `noEmit: false` | Ensure `packages/ui-web/tsconfig.json` has `noEmit: false` and `outDir: "dist"`. |
| ENV `NEXT_PUBLIC_*` is empty at runtime | Not set with `availability: [BUILD]` | Set `[BUILD, RUNTIME]` — these are public vars baked at build time. |
| 500 on every page after deploy | Firebase SDK init fails on missing config | Confirm `NEXT_PUBLIC_FIREBASE_PROJECT_ID` is set on the backend. |
| App Hosting rollout stuck "pending" | Backend not attached to a branch, or no commit since create | `firebase deploy --only apphosting:<id>` forces a rollout. |
| npm install fails on CI with ETARGET | root `package.json` no longer has npm workspaces | Each app installs independently — CI already does `cd apps/<app> && npm install`. |

---

## 8 · End-to-end smoke test

From the App Hosting Staff URL, open `/drill` → **Trigger drill**:

1. Frame ingested (HTTP 202 from `$URL_INGEST/v1/frames`).
2. Vision analyzes via Gemini (`used_gemini: true`).
3. Orchestrator classifies + dispatches.
4. An incident row appears on Home via Firestore live listener.
5. Tapping it opens the detail screen with cascade forecast + dispatch list.
6. Audit rows in BigQuery:

```powershell
bq query --use_legacy_sql=false `
  "SELECT event_time, action, actor_id, venue_id, incident_id, row_hash `
   FROM aegis_audit.events `
   ORDER BY event_time DESC LIMIT 10"
```

Expect `incident.detected`, `incident.classified`, `incident.cascade_predicted`,
`incident.dispatched`, `dispatch.paged` rows with non-null `row_hash` linked
via `prev_hash`.

---

## 9 · Production hardening checklist

- [ ] Tighten CORS on every Cloud Run service — replace `allow_origins=["*"]`
      with the deployed App Hosting origins.
- [ ] Set `AEGIS_REQUIRE_AUTH=1` on production Cloud Run env vars and mount
      `Depends(verify_request)` on write endpoints in Dispatch + Orchestrator.
      Middleware already in `aegis_shared.auth`.
- [ ] Restrict the Google Maps API key's HTTP referrers to the App Hosting
      hostnames.
- [ ] Restrict the Firebase Web API key to the App Hosting hostnames.
- [ ] Remaining high-severity `npm audit` advisories are Next.js 14
      transitive; clearing requires Next 16 upgrade. Scheduled for Phase 2.
- [ ] Enable Firebase App Check, register both origins, set reCAPTCHA v3
      site keys, set `FIREBASE_APP_CHECK_REQUIRED=1`.
- [ ] Confirm Firestore rules + all 4 composite indexes present.
- [ ] Set `minInstances: 1` on both App Hosting backends + orchestrator +
      dispatch Cloud Run services for demo day (eliminates cold starts).

---

## 10 · Rollback

```powershell
# Cloud Run — roll back to a previous revision:
gcloud run services update-traffic aegis-orchestrator `
  --to-revisions=<prev-revision>=100 --region=asia-south1

# App Hosting — roll a backend back to a previous rollout:
firebase apphosting:rollouts:list --backend aegis-staff
firebase apphosting:rollouts:rollback <rollout-id> --backend aegis-staff

# Firestore indexes — redeploy the previous file:
git checkout HEAD~1 -- firebase/firestore.indexes.json
firebase deploy --only firestore:indexes

# Full infra reset (destructive):
cd terraform
terraform destroy
```

---

## 11 · Demo day runbook

Pre-demo (45 min before pitch):

1. `curl https://<each-service>/health` → all 200.
2. Load the staff URL — incidents list shows (even if empty).
3. Run one drill — Gemini path works, live logs visible.
4. If Gemini rate-limits, the heuristic fallback keeps the demo alive;
   trace shows `used_gemini: false`.
5. Keep Cloud Logging open on a second monitor.
6. Have `bq query` ready for the audit chain reveal.
7. Browser tab: `console.firebase.google.com/project/<proj>/firestore`
   on `/incidents` with live updates showing.

Backup: `npm run dev:staff` + `make emulators` runs the whole stack on a
laptop if the deploy breaks mid-pitch.

---

## Appendix A — Environment variables (reference)

All `NEXT_PUBLIC_*` vars are baked into the Next.js bundle at build time
(App Hosting: use `availability: [BUILD, RUNTIME]`).
All backend vars are read by `aegis_shared.config.Settings` at service start.

| Variable | Used by | Example |
|---|---|---|
| `AEGIS_ENV` | All Cloud Run services | `prod` |
| `AEGIS_REQUIRE_AUTH` | All Cloud Run services | `1` |
| `GCP_PROJECT_ID` | All Cloud Run services | `aegis-gsc-2026` |
| `GCP_REGION` | All Cloud Run services | `asia-south1` |
| `VERTEX_AI_LOCATION` | Vision, Orchestrator | `asia-south1` |
| `GOOGLE_API_KEY` | Vision, Orchestrator (dev path) | `AIza...` |
| `FIREBASE_PROJECT_ID` | Dispatch (FCM) | `aegis-gsc-2026` |
| `FIRESTORE_EMULATOR_HOST` | Local dev | `127.0.0.1:8080` |
| `PUBSUB_EMULATOR_HOST` | Local dev | `127.0.0.1:8085` |
| `NEXT_PUBLIC_FIREBASE_*` | App Hosting backends | see §7.3 |
| `NEXT_PUBLIC_INGEST_URL` | Staff drill page | `https://aegis-ingest-...run.app` |
| `NEXT_PUBLIC_VISION_URL` | Staff drill page | `https://aegis-vision-...run.app` |
| `NEXT_PUBLIC_ORCHESTRATOR_URL` | Staff drill page | `https://aegis-orchestrator-...run.app` |
| `NEXT_PUBLIC_DISPATCH_URL` | Staff incident page | `https://aegis-dispatch-...run.app` |
| `NEXT_PUBLIC_DEMO_VENUE_ID` | Web apps | `taj-ahmedabad` |

---

## Appendix B — Debugging the deploy

| Symptom | Most likely cause | Fix |
|---|---|---|
| `gcloud run deploy` fails with `imagepull` | Artifact Registry image missing | Rerun `.\scripts\deploy.ps1`; check `gcloud builds list --limit=5`. |
| Orchestrator returns 500 on first request | `aegis-agents` missing from container | Verify `services/orchestrator/Dockerfile` has `COPY agents /app/agents` + `RUN pip install /app/agents`. Rebuild. |
| Vision returns OTHER/0.05 on every frame | Gemini creds missing | Check `GOOGLE_API_KEY` env OR service account has `roles/aiplatform.user`. |
| App Hosting build fails `@aegis/ui-web not found` | Stale or missing tgz | `.\scripts\pack-ui.ps1`, commit tgz, push. |
| Staff PWA shows `Firebase not configured` | `NEXT_PUBLIC_FIREBASE_*` missing at build time | Set via `firebase apphosting:config:set` or `apphosting.yaml` `env` with `availability: [BUILD, RUNTIME]`. |
| Incident doesn't appear on Home screen | Firestore rules blocking read | Verify `request.auth.token.venues` is populated — trigger `syncCustomClaims` by writing a `/users/{uid}` doc. |
| Pub/Sub messages stuck in DLQ | Subscribers not promoted to push | Re-run §4. |
| BigQuery audit rows missing `row_hash` | Permission issue on service account | Check Cloud Run logs for `audit_bq_write_failed`. |
| App Hosting rollout "pending" forever | No source push since backend create | `firebase deploy --only apphosting:<backendId>` forces a rollout. |

---

## Appendix C — What we deliberately skipped for Phase 1

Phase 2 items, explicitly out of scope:

- MedGemma triage service (§15.4, §33)
- Audio event detection service (§7.1 item 1.4, §29)
- Sensor Fusion service (§30)
- Evacuation planner with min-cost max-flow (§34, §63)
- Multi-lingual PA announcements (§19.2/§19.3, §35)
- Authority webhook service (§19.6, §36)
- Authority console web app (§45)
- Responder Flutter app (§42)
- Guest PWA + on-device sensor fusion (§43, §61)
- Vertex AI ADK migration of the orchestrator (§12.1)
- Learning loop pipeline (§62)

Each is listed in `progress.md` with its Phase 2 priority.

---

*Every second is a life.*
