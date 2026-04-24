resource "google_storage_bucket" "evidence" {
  name                        = "aegis-evidence-${var.env}-${var.project_id}"
  location                    = var.region
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  depends_on                  = [google_project_service.services]

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
    condition {
      age = var.evidence_retention_days
    }
  }

  lifecycle_rule {
    action { type = "Delete" }
    condition {
      age = 180
    }
  }
}

resource "google_storage_bucket" "reports" {
  name                        = "aegis-reports-${var.env}-${var.project_id}"
  location                    = var.region
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  depends_on                  = [google_project_service.services]

  versioning {
    enabled = true
  }

  # Regulatory: 7-year retention on generated PDF reports (blueprint §17.3).
  retention_policy {
    retention_period = 86400 * 365 * 7
  }
}

resource "google_storage_bucket" "assets" {
  name                        = "aegis-venue-assets-${var.env}-${var.project_id}"
  location                    = var.region
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  depends_on                  = [google_project_service.services]
}
