# Aegis · Terraform IaC

Single-root, module-light Terraform that provisions everything Phase 1 needs in
GCP. Targeted at a **single project** (e.g. `aegis-gsc-2026`) in
`asia-south1`. Phase 2 promotes this to a folder with dev/staging/prod stacks.

## What gets created

- **APIs enabled** — Pub/Sub, Cloud Run, Artifact Registry, BigQuery, Firestore,
  Cloud Build, Cloud Storage, IAM, Secret Manager, Vertex AI.
- **Pub/Sub topics + subscriptions** with DLQ for every hot path:
  `raw-frames`, `audio-chunks`, `sensor-events`, `perceptual-signals`,
  `incident-events`, `dispatch-events`, `audit-events`.
- **BigQuery dataset** `aegis_audit` with the append-only `events` table
  (partitioned by `DATE(event_time)`, clustered on `venue_id, incident_id`).
- **Cloud Storage buckets** — `aegis-evidence-<env>`, `aegis-reports-<env>`,
  `aegis-venue-assets-<env>` with uniform bucket-level access ON.
- **Artifact Registry** Docker repo `aegis` in `asia-south1`.
- **Service accounts + IAM bindings** per-service (least privilege).
- **Secret Manager** placeholders for SendGrid / MSG91 / authority signing key.

## Quickstart

```powershell
cd terraform

# one-time: create a GCS bucket for remote state (terraform state bucket)
gcloud storage buckets create gs://aegis-tf-state-$env:USER `
  --location=asia-south1 --uniform-bucket-level-access

# copy the example vars and fill in your project id
Copy-Item terraform.tfvars.example terraform.tfvars
notepad terraform.tfvars

terraform init -backend-config="bucket=aegis-tf-state-$env:USER"
terraform plan -out=tfplan
terraform apply tfplan
```

## Files

| File | Purpose |
|------|---------|
| `versions.tf` | Pinned provider versions + backend config |
| `variables.tf` | Project id, region, env, dataset names |
| `apis.tf` | `google_project_service` for every API Aegis needs |
| `pubsub.tf` | All topics + subscriptions + DLQs |
| `bigquery.tf` | `aegis_audit.events` table schema |
| `storage.tf` | Evidence, reports, venue asset buckets |
| `artifact_registry.tf` | Docker repo |
| `iam.tf` | Per-service service accounts + bindings |
| `secrets.tf` | Secret Manager placeholders |
| `outputs.tf` | Key URIs printed after `apply` |

## Post-apply checklist

1. Deploy the services: `.\scripts\deploy.ps1` from the repo root.
2. Update each Pub/Sub push subscription's `push_endpoint` to the deployed
   Cloud Run URL (pushed automatically via `null_resource` lifecycle if you
   re-run `terraform apply` after deploy).
3. Populate secrets: `gcloud secrets versions add sendgrid-api-key --data-file=-`
4. Push Firestore rules + indexes: `.\scripts\deploy_firebase.ps1`
