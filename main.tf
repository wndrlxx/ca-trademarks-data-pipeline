terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.22.0"
    }
  }
}

provider "google" {
  credentials = file(var.keyfile)
  project     = var.project
  region      = var.region
}

resource "google_storage_bucket" "raw" {
  name          = var.gcs_bucket_name
  location      = var.location
  project       = var.project
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}
