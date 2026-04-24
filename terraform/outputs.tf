output "project_id" {
  value = var.project_id
}

output "region" {
  value = var.region
}

output "artifact_repo" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_repo}"
}

output "evidence_bucket" {
  value = google_storage_bucket.evidence.name
}

output "reports_bucket" {
  value = google_storage_bucket.reports.name
}

output "audit_table" {
  value = "${var.project_id}.${google_bigquery_dataset.audit.dataset_id}.${google_bigquery_table.audit_events.table_id}"
}

output "service_accounts" {
  value = { for k, sa in google_service_account.service_sa : k => sa.email }
}

output "pubsub_topics" {
  value = [for t in google_pubsub_topic.topic : t.name]
}
