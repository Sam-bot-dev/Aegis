# Aegis — Deployment Guide
### Phase 1 production deploy · last updated 2026-04-24

> **Prereq:** `SETUP.md` is completed end-to-end. This document picks up from a
> green local environment and walks you through everything needed to stand Aegis
> up on real infrastructure, in the right order, with the right verification
> checks after each step.

---

## Platform recommendation

| Surface | Where | Why |
|---|---|---|
| **Python services** (ingest / vision / orchestrator / dispatch) | **Cloud Run** (asia-south1) | Blueprint §16.1 — per-request billing, auto-scale, CPU-always for hot paths, tight Pub/Sub / Firestore / Vertex AI integration. Region matters: asia-south1 is closest to Indian venues (≤40 ms p50). |
| **Next.js web apps** (staff PWA, venue dashboard) | **Firebase Hosting** (primary) or **Vercel** (fallback) | Firebase Hosting is the right default because it co-locates with Firestore / Auth / FCM and uses Google-issued certs automatically. Vercel is fine if you prefer its DX, but you'll pay an extra cross-cloud hop on every Firestore/Auth call (measurable; typically 30-60ms). **For the judge demo, prefer Firebase Hosting.** |
| **Firestore + Auth + FCM + Cloud Functions** | **Firebase** (same GCP project) | Already created in `SETUP.md`. |
| **Pub/Sub, BigQuery, Cloud Storage, Artifact Registry, Secret Manager** | **GCP** (Terraform) | One `terraform apply` creates all of them. |

**Do NOT deploy backend to Vercel or Render.** Our backend is stateful (Pub/Sub
subscriptions, Firestore listeners, FCM), needs Google-issued service account
credentials for Gemini + BigQuery + DLP, and the event-driven architecture
requires Pub/Sub push subscriptions targeting a stable HTTPS URL — exactly
what Cloud Run provides for free. Running it elsewhere would force custom
IAM glue + cross-cloud egress fees + worse latency.

---

## 0 · One-time prep (15 min)

Verify every prereq:

```powershell
gcloud --version                # ≥ 510
firebase --version              # ≥ 13
docker --version
terraform --version 2>$null     # if missing:  winget install HashiCorp.Terraform
gcloud config get-value project # should be: aegis-gsc-2026 (or yours)
gcloud auth list                # your user account must be active
gcloud auth application-default print-access-token > $null  # ADC must work
```

Make sure required APIs are enabled (`SETUP.md` Part 2 covers this; Terraform
will re-enable anyway). Confirm billing is linked.

**Sanity check — local still green:**

```powershell
# From repo root
python -m ruff check .
python -m ruff format --check services agents tests
python -m mypy services agents
pytest -q
npm --workspace packages/ui-web run test
npm run build:staff
npm run build:dashboard
```

If any of these fail, **do not proceed**. Fix locally first.

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

# Create tfvars from the example.
Copy-Item terraform.tfvars.example terraform.tfvars
notepad terraform.tfvars    # set project_id, region, env

terraform init -backend-config="bucket=aegis-tf-state-<your-name>"
terraform plan -out=tfplan
terraform apply tfplan

# Record the outputs.
terraform output
```

**Verification:**

```powershell
gcloud pubsub topics list --filter="name~aegis" | findstr /c:"raw-frames"
gcloud pubsub topics list --filter="name~aegis" | findstr /c:"dispatch-events"
bq ls aegis_audit
gcloud storage buckets list --filter="name~aegis"
gcloud artifacts repositories list --location=asia-south1
gcloud iam service-accounts list --filter="email~aegis-"
```

All six commands should return results.

**If this step fails** — the typical cause is missing IAM. You need
`roles/owner` or each of these individually on the project:
`roles/pubsub.admin`, `roles/bigquery.admin`, `roles/storage.admin`,
`roles/iam.serviceAccountAdmin`, `roles/artifactregistry.admin`,
`roles/secretmanager.admin`, `roles/serviceusage.serviceUsageAdmin`.

---

## 2 · Populate secrets

Terraform only creates the secret *shells*. Each secret must be filled in
before the services start:

```powershell
# Service-to-service HMAC (generate a random 48-byte base64 string).
$s = [Convert]::ToBase64String((1..48 | ForEach-Object {Get-Random -Max 256}))
$s | gcloud secrets versions add service-internal-secret --data-file=-

# Authority-webhook Ed25519 signing key (Phase 2 needs it, placeholder for now).
openssl genpkey -algorithm ed25519 -out /tmp/aegis-webhook.pem
Get-Content /tmp/aegis-webhook.pem | `
  gcloud secrets versions add authority-webhook-signing-key --data-file=-

# SendGrid + MSG91 are Phase 2 (guest SMS / authority email) — leave until then
# or put a placeholder string to prevent Cloud Run from failing on missing:
"placeholder" | gcloud secrets versions add sendgrid-api-key --data-file=-
"placeholder" | gcloud secrets versions add msg91-auth-key --data-file=-
```

---

## 3 · Build + deploy Cloud Run services

```powershell
# From repo root.
.\scripts\deploy.ps1
```

This script (see `scripts/deploy.ps1`) for each of ingest / vision /
orchestrator / dispatch:

1. Builds the Docker image via **Cloud Build** with the repo root as the build
   context (buildpacks can't resolve the sibling `aegis-agents` path source).
2. Pushes to Artifact Registry `asia-south1-docker.pkg.dev/<proj>/aegis/<svc>`.
3. Deploys to Cloud Run with `--set-env-vars AEGIS_ENV=prod,GCP_PROJECT_ID=…`.
4. Attaches the service account Terraform created (`aegis-<svc>@…`).

**Expected output** — 4 successful deploys and a service URL table at the end:

```
NAME                  URL
aegis-ingest          https://aegis-ingest-xxx.a.run.app
aegis-vision          https://aegis-vision-xxx.a.run.app
aegis-orchestrator    https://aegis-orchestrator-xxx.a.run.app
aegis-dispatch        https://aegis-dispatch-xxx.a.run.app
```

**Verification — each service must return healthy:**

```powershell
$urls = gcloud run services list --region=asia-south1 --format="value(metadata.name,status.url)"
foreach ($line in $urls) {
  $parts = $line -split "`t"
  $url = $parts[1]
  Invoke-WebRequest "$url/health" -UseBasicParsing | Select StatusCode,Content
}
```

Every service should return `200 {"status":"ok","service":"<name>"}`.

**If a service fails to start** — almost always either missing
`aegis-agents` install (orchestrator only) or missing Gemini API key. Check:

```powershell
gcloud run services logs read aegis-orchestrator --region=asia-south1 --limit=50
```

The orchestrator needs `GOOGLE_API_KEY` (Developer API path) or ADC with
`roles/aiplatform.user` (Vertex AI path). Terraform grants the latter. Confirm
with:

```powershell
gcloud run services describe aegis-orchestrator --region=asia-south1 `
  --format="value(spec.template.spec.serviceAccountName)"
# Expect: aegis-orchestrator@<proj>.iam.gserviceaccount.com
```

---

## 4 · Promote pull subscriptions to push

After Cloud Run is up, convert the Terraform-declared pull subscriptions into
push subscriptions pointing at the deployed URLs. Two ways:

### Fast path (gcloud, immediate)

```powershell
$PROJECT = gcloud config get-value project
$URL_VISION  = gcloud run services describe aegis-vision       --region=asia-south1 --format="value(status.url)"
$URL_ORCH    = gcloud run services describe aegis-orchestrator --region=asia-south1 --format="value(status.url)"
$URL_DSP     = gcloud run services describe aegis-dispatch     --region=asia-south1 --format="value(status.url)"

gcloud pubsub subscriptions modify-push-config raw-frames-pull `
  --push-endpoint="$URL_VISION/pubsub/raw-frames"

gcloud pubsub subscriptions modify-push-config perceptual-signals-pull `
  --push-endpoint="$URL_ORCH/pubsub/perceptual-signals"

gcloud pubsub subscriptions modify-push-config dispatch-events-pull `
  --push-endpoint="$URL_DSP/pubsub/dispatch-events"
```

### Right path (Terraform, reproducible)

Add these URLs as tfvars and extend `terraform/pubsub.tf`:

```hcl
variable "vision_url" { type = string }
variable "orchestrator_url" { type = string }
variable "dispatch_url" { type = string }

# Inside the relevant google_pubsub_subscription.pull resource:
push_config {
  push_endpoint = var.vision_url + "/pubsub/raw-frames"
  oidc_token {
    service_account_email = google_service_account.service_sa["aegis-vision"].email
  }
}
```

Then `terraform apply -var=vision_url=…` etc.

---

## 5 · Seed the demo venue

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = ".\.secrets\service-account.json"
python scripts/seed_venue.py config/venues/taj-ahmedabad.json --prod
```

This writes the blueprint §24.1 venue doc + zones + cameras + sensors +
responders. **Verify:**

```powershell
gcloud firestore databases describe --database="(default)"
firebase firestore:indexes
# Or:
gcloud firestore export gs://<bucket>/smoke-export --collection-ids=venues
```

---

## 6 · Push Firebase rules, indexes, and the custom-claims Cloud Function

```powershell
.\scripts\deploy_firebase.ps1
# or directly:
firebase deploy --only firestore:rules,firestore:indexes,functions
```

**Verification:**

```powershell
firebase firestore:indexes | Select-Object -First 20
gcloud functions list --v2 --regions=asia-south1
# Expect: syncCustomClaims ... ACTIVE
```

Test the trigger:

```powershell
# Write a user doc in the Firebase console at /users/test-uid with:
#   { role: "staff", venues: ["taj-ahmedabad"], skills: ["FIRE_WARDEN"] }
# Then check the token:
firebase auth:export /tmp/users.json --project=<proj>
```

The `customClaims` block for `test-uid` should contain `role: "staff"`.

---

## 7 · Deploy the web apps

### Option A — Firebase Hosting (recommended)

Two hosting sites, one project. Add to `firebase.json`:

```json
{
  "hosting": [
    {
      "target": "staff",
      "public": "apps/staff/.next-export",
      "ignore": ["firebase.json", "**/.*", "**/node_modules/**"]
    },
    {
      "target": "dashboard",
      "public": "apps/dashboard/.next-export",
      "ignore": ["firebase.json", "**/.*", "**/node_modules/**"]
    }
  ]
}
```

Then:

```powershell
firebase target:apply hosting staff aegis-staff-<proj>
firebase target:apply hosting dashboard aegis-dashboard-<proj>

# Next.js to static export (our apps are client-rendered, this works):
$env:NEXT_PUBLIC_FIREBASE_PROJECT_ID = "<your-proj>"
$env:NEXT_PUBLIC_FIREBASE_API_KEY    = "<web-api-key>"      # from Firebase console
$env:NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN = "<proj>.firebaseapp.com"
$env:NEXT_PUBLIC_FIREBASE_APP_ID     = "<app-id>"
$env:NEXT_PUBLIC_INGEST_URL          = "$URL_INGEST"
$env:NEXT_PUBLIC_VISION_URL          = "$URL_VISION"
$env:NEXT_PUBLIC_ORCHESTRATOR_URL    = "$URL_ORCH"
$env:NEXT_PUBLIC_DISPATCH_URL        = "$URL_DSP"
$env:NEXT_PUBLIC_DEMO_VENUE_ID       = "taj-ahmedabad"

npm --workspace apps/staff run build
npm --workspace apps/dashboard run build

firebase deploy --only hosting:staff,hosting:dashboard
```

After deploy you get `https://aegis-staff-<proj>.web.app` and
`https://aegis-dashboard-<proj>.web.app`. These are the **public demo URLs**
for the submission.

### Option B — Vercel (fallback)

If Firebase Hosting isn't working for you:

```powershell
npm install -g vercel
cd apps/staff
vercel --prod `
  --env NEXT_PUBLIC_FIREBASE_PROJECT_ID=<your-proj> `
  --env NEXT_PUBLIC_FIREBASE_API_KEY=<web-api-key> `
  --env NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=<proj>.firebaseapp.com `
  --env NEXT_PUBLIC_FIREBASE_APP_ID=<app-id> `
  --env NEXT_PUBLIC_INGEST_URL=$URL_INGEST `
  --env NEXT_PUBLIC_VISION_URL=$URL_VISION `
  --env NEXT_PUBLIC_ORCHESTRATOR_URL=$URL_ORCH `
  --env NEXT_PUBLIC_DISPATCH_URL=$URL_DSP `
  --env NEXT_PUBLIC_DEMO_VENUE_ID=taj-ahmedabad

cd ../dashboard
vercel --prod <same env args>
```

Caveats:
1. Vercel's Next.js runtime auto-adds a CDN edge, which is good, but cold starts
   can hit 1.5–2 s for our bundle size. Firebase Hosting is usually faster for
   this size.
2. Vercel's free tier is fine for demo traffic. If you expect > 100 k hits
   during the judge day, check usage limits.
3. CORS — every Cloud Run service must allow `https://*.vercel.app` and your
   custom domain. The FastAPI CORS middleware is already `allow_origins=["*"]`
   in `services/*/main.py`; tighten before any serious traffic.

**Do NOT deploy the Next.js apps to Render.** Render cold-starts are minutes on
the free tier; Vercel / Firebase Hosting are seconds. The backend is on Cloud
Run either way.

---

## 8 · End-to-end smoke test

From the deployed demo URL, click **Drill** → **Trigger drill**. Expected:

1. Frame ingested (HTTP 202 from `$URL_INGEST/v1/frames`).
2. Vision analyzes via Gemini (`used_gemini: true` on the response).
3. Orchestrator classifies + dispatches (incident id returned).
4. An incident row appears on the Home screen via Firestore live listener.
5. Clicking the incident opens the detail screen with the cascade forecast and
   dispatch list, updating in real time.
6. Audit rows land in BigQuery:

```powershell
bq query --use_legacy_sql=false `
  "SELECT event_time, action, actor_id, venue_id, incident_id, row_hash `
   FROM aegis_audit.events `
   ORDER BY event_time DESC LIMIT 10"
```

Expect `incident.detected`, `incident.classified`, `incident.cascade_predicted`,
`incident.dispatched`, `dispatch.paged` rows — one per agent hop, each with a
non-null `row_hash` linked via `prev_hash`.

**Chain integrity check:**

```powershell
python -c "from aegis_shared.audit import verify_chain_local; print(verify_chain_local())"
# Expect: (True, [])
```

---

## 9 · Production hardening checklist

Before sharing the demo URL publicly:

- [ ] Tighten CORS on every Cloud Run service — replace `allow_origins=["*"]`
  with the deployed web-app origins.
- [ ] Set `AEGIS_REQUIRE_AUTH=1` on production Cloud Run env vars and mount
  `Depends(verify_request)` on every write endpoint in Dispatch + Orchestrator.
  The middleware is already in `aegis_shared.auth`; the wiring is a one-line
  change per route (`principal: Principal = Depends(verify_request)`).
- [ ] Restrict the Google Maps API key's HTTP referrers to your deployed
  hosting domains (blueprint §18.1 quarter-rotation).
- [ ] Restrict the Firebase Web API key to the deployed domains too.
- [ ] Review `npm audit`. Five high-severity transitive advisories remain in
  Next.js 14 (`GHSA-q4gf-8mx6-v5v3` class). Clearing requires Next.js 16
  upgrade (breaking change). Accept for Phase 1 submission; schedule for
  Phase 2.
- [ ] Enable Firebase App Check in the console, register both web apps, set
  reCAPTCHA v3 site keys, and set `FIREBASE_APP_CHECK_REQUIRED=1` on Cloud Run.
- [ ] Confirm the Firestore rules deploy completed (`firebase firestore:indexes`
  must list all 4 composite indexes; rules show up at the Firebase console).
- [ ] Set `min_instances = 1` on orchestrator + dispatch (currently 0 to save
  cost; minimum 1 eliminates cold-start latency during live judge demos).

---

## 10 · Rollback

If anything goes wrong with a deploy:

```powershell
# Roll Cloud Run back to the previous revision:
gcloud run services update-traffic aegis-orchestrator `
  --to-revisions=<prev-revision>=100 --region=asia-south1

# Roll Firebase Hosting back to previous release:
firebase hosting:clone <proj>:staff --release <release-id>

# Roll Firestore indexes (no rollback — redeploy the previous indexes file).
git checkout HEAD~1 -- firebase/firestore.indexes.json
firebase deploy --only firestore:indexes
```

For a hard reset of everything Terraform created:

```powershell
cd terraform
terraform destroy   # destructive — wipes Pub/Sub, BigQuery, buckets, SAs
```

---

## 11 · Demo day runbook

Pre-demo checklist (45 min before pitch):

1. Confirm all 4 Cloud Run services return 200 on `/health`.
2. Confirm the staff PWA opens and shows the incident list (even if empty).
3. Run one drill from `/drill` — verify Gemini path works (live token usage
   visible in `gcloud run services logs`).
4. If Gemini is slow / rate-limited: the heuristic fallback still produces a
   valid incident; the UI will just show `used_gemini: false` in the trace.
5. Keep the Cloud Logging tab open in a second monitor — judges love live logs.
6. Have `bq query` ready for the audit chain reveal.
7. Browser tab ready: `console.firebase.google.com/project/<proj>/firestore`
   showing the `/incidents` collection live.

If the demo URL fails mid-pitch: open localhost (`npm run dev:staff` from repo
root with emulators running). The full stack works on a laptop.

---

## Appendix A — Environment variables (reference)

All `NEXT_PUBLIC_*` vars are baked into the Next.js bundle at build time.
All backend vars are read by `aegis_shared.config.Settings` at service start.

| Variable | Used by | Example |
|---|---|---|
| `AEGIS_ENV` | All services | `prod` |
| `AEGIS_REQUIRE_AUTH` | All services | `1` (prod) |
| `GCP_PROJECT_ID` | All services | `aegis-gsc-2026` |
| `GCP_REGION` | All services | `asia-south1` |
| `VERTEX_AI_LOCATION` | Vision, Orchestrator | `asia-south1` |
| `GOOGLE_API_KEY` | Vision, Orchestrator (dev only) | `AIza...` |
| `FIREBASE_PROJECT_ID` | Dispatch (FCM) | `aegis-gsc-2026` |
| `FIRESTORE_EMULATOR_HOST` | Local dev | `127.0.0.1:8080` |
| `PUBSUB_EMULATOR_HOST` | Local dev | `127.0.0.1:8085` |
| `NEXT_PUBLIC_FIREBASE_*` | Web apps | see Part 7 |
| `NEXT_PUBLIC_INGEST_URL` | Web drill page | `https://aegis-ingest-...run.app` |
| `NEXT_PUBLIC_VISION_URL` | Web drill page | `https://aegis-vision-...run.app` |
| `NEXT_PUBLIC_ORCHESTRATOR_URL` | Web drill page | `https://aegis-orchestrator-...run.app` |
| `NEXT_PUBLIC_DISPATCH_URL` | Staff incident page | `https://aegis-dispatch-...run.app` |
| `NEXT_PUBLIC_DEMO_VENUE_ID` | Web apps | `taj-ahmedabad` |

---

## Appendix B — Debugging the deploy

| Symptom | Most likely cause | Fix |
|---|---|---|
| `gcloud run deploy` fails with `imagepull` error | Artifact Registry image missing | Rerun `scripts/deploy.ps1`; it builds then deploys. Check `gcloud builds list --limit=5` for the Cloud Build job. |
| Orchestrator returns 500 on first request | `aegis-agents` missing from container | Verify `services/orchestrator/Dockerfile` has `COPY agents /app/agents` + `RUN pip install /app/agents`. Rebuild. |
| Vision service OTHER/0.05 on every frame | Gemini creds missing | Check env var `GOOGLE_API_KEY` OR that service account has `roles/aiplatform.user`. |
| Staff PWA shows `Firebase not configured` | `NEXT_PUBLIC_FIREBASE_*` missing at build time | Rebuild with env vars set; they bake in at build time, not runtime. |
| Incident doesn't appear on Home screen | Firestore rules blocking read | Inspect `request.auth.token.venues` in the Firebase Auth console; may need to trigger `syncCustomClaims` by writing the user doc. |
| Pub/Sub messages stuck in DLQ | Subscribers not promoted to push, or Cloud Run URL wrong | Re-run the `modify-push-config` block in Part 4. |
| BigQuery audit rows missing `row_hash` | `aegis_shared.audit.write_audit` not called inside the audit code path | Check Cloud Run logs for `audit_bq_write_failed`; usually a permissions issue on the service account. |

---

## Appendix C — What we deliberately skipped for Phase 1

The blueprint describes a much larger system than Phase 1 requires. These are
Phase 2 items, explicitly out of scope here:

- MedGemma triage service (§15.4, §33)
- Audio event detection service (§7.1 item 1.4, §29)
- Sensor Fusion service (§30)
- Evacuation planner with min-cost max-flow (§34, §63)
- Multi-lingual PA announcements (§19.2, §19.3, §35)
- Authority webhook service (§19.6, §36)
- Authority console web app (§45)
- Responder Flutter app (§42)
- Guest PWA + on-device sensor fusion (§43, §61)
- Vertex AI ADK migration of the orchestrator (§12.1)
- Learning loop pipeline (§62)
- Cascade-aware re-routing of dispatches (§59 is done; re-routing is Phase 2)

Every one of these is listed in `progress.md` with its Phase 2 priority.

---

*Every second is a life.*
