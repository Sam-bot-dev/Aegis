# Secret Manager placeholders. Populate with:
#
#   echo -n "<value>" | gcloud secrets versions add <name> --data-file=-

locals {
  secrets = [
    "sendgrid-api-key",
    "msg91-auth-key",
    "authority-webhook-signing-key",
    "service-internal-secret",
  ]
}

resource "google_secret_manager_secret" "secret" {
  for_each  = toset(local.secrets)
  secret_id = each.key
  replication {
    auto {}
  }
  depends_on = [google_project_service.services]
}
