locals {
  required_apis = [
    "aiplatform.googleapis.com",
    "generativelanguage.googleapis.com",
    "firestore.googleapis.com",
    "firebase.googleapis.com",
    "identitytoolkit.googleapis.com",
    "fcm.googleapis.com",
    "pubsub.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "storage.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudtasks.googleapis.com",
    "cloudscheduler.googleapis.com",
    "cloudkms.googleapis.com",
    "dlp.googleapis.com",
    "translate.googleapis.com",
    "texttospeech.googleapis.com",
    "speech.googleapis.com",
    "bigquery.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
  ]
}

resource "google_project_service" "services" {
  for_each                   = toset(local.required_apis)
  service                    = each.key
  disable_on_destroy         = false
  disable_dependent_services = false
}
