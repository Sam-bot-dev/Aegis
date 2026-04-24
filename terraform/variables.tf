variable "project_id" {
  type        = string
  description = "GCP project id (e.g. aegis-gsc-2026)."
}

variable "region" {
  type        = string
  default     = "asia-south1"
  description = "Primary region (Mumbai = fastest for Indian venues)."
}

variable "env" {
  type        = string
  default     = "prod"
  description = "Environment tag (local|dev|staging|prod). Used in bucket names."
}

variable "bq_audit_dataset" {
  type    = string
  default = "aegis_audit"
}

variable "bq_analytics_dataset" {
  type    = string
  default = "aegis_analytics"
}

variable "bq_learning_dataset" {
  type    = string
  default = "aegis_learning"
}

variable "cloud_run_services" {
  type = list(string)
  default = [
    "aegis-ingest",
    "aegis-vision",
    "aegis-orchestrator",
    "aegis-dispatch",
  ]
  description = "Service accounts created one-per-service."
}

variable "artifact_repo" {
  type    = string
  default = "aegis"
}

variable "ack_deadline_seconds" {
  type        = number
  default     = 30
  description = "Default Pub/Sub ack deadline."
}

variable "evidence_retention_days" {
  type        = number
  default     = 30
  description = "Days before evidence frames move to Coldline."
}
