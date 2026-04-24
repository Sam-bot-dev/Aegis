resource "google_artifact_registry_repository" "aegis" {
  location      = var.region
  repository_id = var.artifact_repo
  description   = "Aegis service images (Cloud Run)."
  format        = "DOCKER"
  depends_on    = [google_project_service.services]
}
