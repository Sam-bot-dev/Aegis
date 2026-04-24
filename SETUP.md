# Aegis — Setup Guide

> **Read this file top-to-bottom before running any command in the repo.**
> Estimated time: ~30 minutes first time, ~5 minutes for teammates you onboard later.

By the end of this guide you will have:

- Every local tool installed (Python, Node, Docker, gcloud, Firebase CLI, uv)
- A working Google Cloud project with all required APIs enabled
- A service-account key downloaded to `.secrets/`
- A Firebase project linked to the GCP project
- A Gemini API key for fast local dev
- A Google Maps API key for the apps
- The Aegis monorepo installed and running locally
- A successful end-to-end smoke test

---

## Part 1 — Install local tools (Windows)

Open **PowerShell as Administrator** and run the commands below.

```powershell
winget install -e --id Python.Python.3.12
winget install -e --id Git.Git
winget install -e --id OpenJS.NodeJS.LTS
winget install -e --id Docker.DockerDesktop
winget install -e --id Google.CloudSDK
winget install -e --id Microsoft.VisualStudioCode
```

Close and re-open PowerShell (so `PATH` picks up the new installs), then:

```powershell
npm install -g firebase-tools
pip install uv
```

Verify everything:

```powershell
python --version        # 3.12.x
node --version          # v20.x
docker --version        # any modern version
gcloud --version        # includes components list
firebase --version      # 13.x or newer
uv --version
```

**Open Docker Desktop once** (double-click the shortcut) and let it finish starting. The docker daemon must be running before the emulators work.

If `winget` is missing on older Windows 10: install it via the Microsoft Store ("App Installer"), reboot, retry.

---

## Part 2 — Create the Google Cloud project

Pick a globally-unique project ID (letters, numbers, hyphens; 6–30 chars). Example below uses `aegis-gsc-2026` — substitute your own if that's taken.

```powershell
gcloud auth login
gcloud auth application-default login

gcloud projects create aegis-gsc-2026 --name="Aegis"
gcloud config set project aegis-gsc-2026
```

### Link billing

1. Go to [console.cloud.google.com/billing](https://console.cloud.google.com/billing)
2. If you have no billing account yet, click **Create account** and add a card — you get **$300 in free credits for 90 days** as a new user
3. Link the billing account to `aegis-gsc-2026`

Without billing linked, every API call below fails with `BILLING_DISABLED`. You will not be charged during this hackathon — the free tier plus your $300 trial covers orders of magnitude more than we'll use. The Solution Challenge also provides additional Google Cloud credits to the Top 100 teams in Phase 2.

### Enable the APIs Aegis needs

Paste this entire block (PowerShell handles the backticks as line continuations):

```powershell
gcloud services enable `
  aiplatform.googleapis.com `
  generativelanguage.googleapis.com `
  firestore.googleapis.com `
  firebase.googleapis.com `
  identitytoolkit.googleapis.com `
  fcm.googleapis.com `
  pubsub.googleapis.com `
  cloudbuild.googleapis.com `
  run.googleapis.com `
  artifactregistry.googleapis.com `
  storage.googleapis.com `
  secretmanager.googleapis.com `
  cloudtasks.googleapis.com `
  cloudscheduler.googleapis.com `
  cloudkms.googleapis.com `
  dlp.googleapis.com `
  translate.googleapis.com `
  texttospeech.googleapis.com `
  speech.googleapis.com `
  maps-backend.googleapis.com `
  places-backend.googleapis.com `
  routes.googleapis.com `
  geocoding-backend.googleapis.com `
  bigquery.googleapis.com `
  logging.googleapis.com `
  monitoring.googleapis.com
```

This takes ~60 seconds. Grab a coffee.

---

## Part 3 — Service account (for local dev)

Aegis services authenticate to Google APIs using a service account in local dev. In production they use Workload Identity (no key file needed) — we set that up in Phase 2.

```powershell
cd C:\Users\mekha\OneDrive\Desktop\Projects\Aegis

# Create the service account
gcloud iam service-accounts create aegis-dev `
  --display-name="Aegis local dev"

# Grant the roles it needs (broad for dev, narrowed for prod later)
$PROJECT = "aegis-gsc-2026"
$SA = "aegis-dev@$PROJECT.iam.gserviceaccount.com"

foreach ($role in @(
  "roles/aiplatform.user",
  "roles/datastore.user",
  "roles/pubsub.editor",
  "roles/storage.admin",
  "roles/logging.logWriter",
  "roles/secretmanager.secretAccessor",
  "roles/cloudtranslate.user",
  "roles/bigquery.dataEditor",
  "roles/bigquery.jobUser"
)) {
  gcloud projects add-iam-policy-binding $PROJECT `
    --member="serviceAccount:$SA" --role=$role
}

# Create the .secrets folder and download the key there
New-Item -ItemType Directory -Force -Path .\.secrets | Out-Null
gcloud iam service-accounts keys create .\.secrets\service-account.json `
  --iam-account=$SA
```

**Critical:** `.secrets/` is gitignored. Never commit this file. If you think it leaked, rotate immediately:

```powershell
gcloud iam service-accounts keys list --iam-account=$SA
gcloud iam service-accounts keys delete <KEY_ID> --iam-account=$SA
```

---

## Part 4 — Firebase

Firebase and GCP share the same project; we just need to enable Firebase features on top.

```powershell
firebase login
firebase use --add   # pick aegis-gsc-2026, alias as "default"
```

Now in a browser:

1. Open [console.firebase.google.com](https://console.firebase.google.com) → click your `aegis-gsc-2026` project
2. **Build → Firestore Database → Create database**
   - Mode: **Native** (not Datastore)
   - Location: **asia-south1 (Mumbai)** — closest to India, fastest for users
   - Start in **production mode** (rules already in the repo)
3. **Build → Authentication → Get started**
   - Enable **Phone** provider (staff/responder login)
   - Enable **Email/Password** provider (corporate dashboard login)
4. **Build → Cloud Messaging** — already enabled, just note the Server Key is auto-managed now via FCM v1
5. **Project settings (gear icon) → Service accounts → Generate new private key**
   - Save the file as `.secrets\firebase-adminsdk.json` in your repo root

Push the Firestore rules + indexes from the repo:

```powershell
firebase deploy --only firestore:rules,firestore:indexes
```

You should see `✓ Deploy complete!`.

---

## Part 5 — Gemini API key (fast path for Phase 1 dev)

For Phase 1 we use the Gemini Developer API directly (simpler auth, same models). For Phase 2 we switch to Vertex AI — the `GeminiClient` in `aegis_shared/gemini.py` already supports both, controlled by the env var.

1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Click **Create API key** → select `aegis-gsc-2026` as the project
3. Copy the key (starts with `AIza...`)
4. Save it — you'll paste it into `.env` in Part 7

---

## Part 6 — Google Maps API key

1. Go to [console.cloud.google.com/google/maps-apis/credentials](https://console.cloud.google.com/google/maps-apis/credentials)
2. **Create credentials → API key**
3. Copy the key, then click **Edit API key**
4. **Application restrictions:**
   - For local dev: leave as **None** temporarily
   - Before deploying: set HTTP referrers to `localhost:*/*`, `127.0.0.1:*/*`, `*.aegis.ai/*`
5. **API restrictions → Restrict key** and tick:
   - Maps JavaScript API
   - Maps SDK for Android
   - Maps SDK for iOS
   - Places API
   - Routes API
   - Geocoding API
   - Maps Static API

Save the key for `.env`.

---

## Part 7 — Clone and configure the repo

If you received the repo as a zip, extract it to `C:\Users\mekha\OneDrive\Desktop\Projects\Aegis`. If it's a git repo:

```powershell
cd C:\Users\mekha\OneDrive\Desktop\Projects\Aegis
```

Copy the env template and fill in your values:

```powershell
Copy-Item .env.example .env
notepad .env
```

Fill in at minimum:

```ini
AEGIS_ENV=local
GCP_PROJECT_ID=aegis-gsc-2026
GCP_REGION=asia-south1
GOOGLE_APPLICATION_CREDENTIALS=./.secrets/service-account.json

VERTEX_AI_LOCATION=asia-south1
GOOGLE_API_KEY=AIza...YOUR_GEMINI_KEY_HERE

FIREBASE_PROJECT_ID=aegis-gsc-2026
FIREBASE_ADMIN_CREDENTIALS=./.secrets/firebase-adminsdk.json

FIRESTORE_EMULATOR_HOST=127.0.0.1:8080
PUBSUB_EMULATOR_HOST=127.0.0.1:8085

GOOGLE_MAPS_API_KEY=AIza...YOUR_MAPS_KEY_HERE

SERVICE_INTERNAL_SECRET=<generate any long random string>
```

Save and close notepad.

---

## Part 8 — Install Python dependencies

Run from the repo root:

```powershell
# One-time install of all service deps (via uv, very fast)
make setup
```

If `make` isn't available on Windows, run the commands manually:

```powershell
pip install uv
uv pip install -e services\shared
uv pip install -e services\ingest
uv pip install -e services\vision
uv pip install -e services\orchestrator
uv pip install -e services\dispatch
```

Verify the install:

```powershell
python -c "from aegis_shared import get_settings; print(get_settings().gcp_project_id)"
```

Should print `aegis-gsc-2026`.

---

## Part 9 — Run the local stack

You need two terminals open.

**Terminal 1 — emulators:**

```powershell
make emulators
```

This starts Firestore (`:8080`) and Pub/Sub (`:8085`) emulators in Docker. Leave it running.

**Terminal 2 — services:**

```powershell
.\scripts\dev.ps1
```

Each service opens in its own PowerShell window. When they're all up, you'll see:

```
Aegis local dev stack
  Ingest:       http://localhost:8001/docs
  Vision:       http://localhost:8002/docs
  Orchestrator: http://localhost:8003/docs
  Dispatch:     http://localhost:8004/docs
```

Open the `/docs` URLs in a browser — each is an auto-generated Swagger UI for that service.

---

## Part 10 — Smoke test (end-to-end)

In a **third** terminal:

```powershell
.\scripts\smoke.ps1
```

You should see:

```
== 1/5  Health checks ==
  ✓ http://localhost:8001/health
  ✓ http://localhost:8002/health
  ✓ http://localhost:8003/health
  ✓ http://localhost:8004/health

== 2/5  Frame ingest ==
  ✓ ingest accepted

== 3/5  Vision classify (stub) ==
  ✓ vision classified FIRE

== 4/5  Orchestrator handle ==
  ✓ classified S2
  ✓ dispatched

== 5/5  Dispatch state machine ==
  ✓ ack → ACKNOWLEDGED
  ✓ enroute → EN_ROUTE
  ✓ arrived → ARRIVED

== Done ==
  All systems nominal. You just ran the full Aegis pipeline.
```

**Congratulations — Aegis is running on your machine.** The full data path (Ingest → Vision → Orchestrator → Dispatch via Pub/Sub) is working end-to-end with in-memory stubs that we replace incrementally as Phase 1 progresses.

---

## Part 11 — Run the tests

```powershell
make test
```

All tests should pass. If they don't, `pytest services/<service>/tests/ -v` narrows it down.

---

## Troubleshooting

**`BILLING_DISABLED` error from any `gcloud services` call**
Link a billing account in the console (Part 2) and retry.

**`PermissionDenied: aiplatform.endpoints.predict`**
The service account is missing `roles/aiplatform.user`. Re-run the role-binding loop in Part 3.

**`firebase: command not found` after `npm install -g firebase-tools`**
Close and reopen PowerShell. Verify with `firebase --version`. If still missing, check `npm config get prefix` is on PATH.

**`docker: error during connect: ...`**
Docker Desktop is not running. Open Docker Desktop, wait for the whale icon to stop animating, retry.

**Emulators port already in use (`:8080` or `:8085`)**
Another process is holding those ports. Find and kill it:
```powershell
netstat -ano | findstr :8080
taskkill /PID <pid> /F
```

**Python says `No module named 'aegis_shared'`**
The shared library wasn't installed in editable mode. Run `uv pip install -e services\shared` from the repo root.

**Services crash on startup with `ADC not found`**
`GOOGLE_APPLICATION_CREDENTIALS` in `.env` points to a file that doesn't exist. Check the path (use forward slashes or escaped backslashes).

**`unknown model: gemini-2.5-flash`**
Your `GOOGLE_API_KEY` is from a region where 2.5 isn't yet exposed on the Developer API. Either switch to Vertex AI (unset `GOOGLE_API_KEY` in `.env`) or change the model name to `gemini-1.5-flash` in `.env`.

**Windows line-ending warnings in git**
Run once: `git config --global core.autocrlf input`.

---

## Next steps

Once the smoke test is green:

1. **Read `docs/architecture.md`** for the big picture
2. **Read the blueprint document** — the master spec everything derives from
3. **Claim a feature from the blueprint §7 inventory** based on your role:
   - Ubaid: secure the service-to-service auth path + Terraform skeleton
   - Teammate A: flesh out `/agents/classifier` with the real prompt
   - Teammate B: `flutter create apps/staff` and scaffold the incident-detail screen
   - Teammate C: scaffold the Next.js dashboard in `apps/dashboard`
4. Branch from `main` as `feat/<area>/<short-desc>`, open a PR, get a review, merge

Ship Phase 1 by April 24. Then the real work (Product Vault) begins.

*Every second is a life.*
