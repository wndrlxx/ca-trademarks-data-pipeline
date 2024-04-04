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

resource "google_bigquery_dataset" "ca_trademarks" {
  dataset_id = var.bq_dataset_name
  location   = var.location
}

resource "google_storage_bucket" "ca_trademarks" {
  name          = var.data_bucket_name
  location      = var.location
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

resource "google_storage_bucket" "composer_bucket" {
  name = var.composer_bucket_name
  # Composer bucket must be in the same region as Composer environment
  location      = var.region
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

resource "google_storage_bucket_object" "raw_compressed_folder" {
  name    = "raw/compressed/"
  content = " "
  bucket  = var.data_bucket_name

  depends_on = [google_storage_bucket.ca_trademarks]
}

resource "google_storage_bucket_object" "transformed_folder" {
  name    = "transformed/"
  content = " "
  bucket  = var.data_bucket_name

  depends_on = [google_storage_bucket.ca_trademarks]
}

# upload dags, dbt project, and Spark code to Composer bucket
resource "google_storage_bucket_object" "dags_folder" {
  for_each = fileset("${path.module}/dags", "**/*")

  name   = "dags/${each.key}"
  source = "${path.module}/dags/${each.key}"
  bucket = var.composer_bucket_name

  depends_on = [google_composer_environment.ca_trademarks]
}

# upload include/ directory to Composer bucket
resource "google_storage_bucket_object" "include_folder" {
  for_each = fileset("${path.module}/include", "**/*")

  name   = "include/${each.key}"
  source = "${path.module}/include/${each.key}"
  bucket = var.composer_bucket_name

  depends_on = [google_composer_environment.ca_trademarks]
}

# upload contents of data/ directory to data bucket
resource "google_storage_bucket_object" "raw_data_folder" {
  for_each = fileset("${path.module}/data", "**/*.csv")

  name   = "raw/${each.key}"
  source = "${path.module}/data/${each.key}"
  bucket = var.data_bucket_name

  depends_on = [google_composer_environment.ca_trademarks]
}

resource "google_composer_environment" "ca_trademarks" {
  name   = var.composer_env_name
  region = var.region

  config {
    environment_size = "ENVIRONMENT_SIZE_SMALL"

    software_config {
      image_version = "composer-2.6.5-airflow-2.7.3"
      airflow_config_overrides = {
        "scheduler-dag_dir_list_interval" = "20"
      }
      env_variables = {
        REGION         = var.region
        DATA_BUCKET    = var.data_bucket_name
        AIRFLOW_BUCKET = var.composer_bucket_name
        BQ_DATASET     = var.bq_dataset_name
      }
    }

    node_config {
      service_account = google_service_account.composer-sa.name
    }
  }

  storage_config {
    bucket = var.composer_bucket_name
  }

  depends_on = [google_storage_bucket.composer_bucket, google_service_account.composer-sa]
}

resource "google_service_account" "composer-sa" {
  account_id   = "composer-env-account"
  display_name = "Service account for Composer environment"
}

resource "google_project_iam_member" "composer-worker" {
  project    = var.project
  role       = "roles/composer.worker"
  member     = "serviceAccount:${google_service_account.composer-sa.email}"
  depends_on = [google_service_account.composer-sa]
}

resource "google_project_iam_member" "bigquery-admin" {
  project    = var.project
  role       = "roles/bigquery.admin"
  member     = "serviceAccount:${google_service_account.composer-sa.email}"
  depends_on = [google_service_account.composer-sa]
}

resource "google_project_iam_member" "dataflow-admin" {
  project    = var.project
  role       = "roles/dataflow.admin"
  member     = "serviceAccount:${google_service_account.composer-sa.email}"
  depends_on = [google_service_account.composer-sa]
}

resource "google_project_iam_member" "dataproc-admin" {
  project    = var.project
  role       = "roles/dataproc.admin"
  member     = "serviceAccount:${google_service_account.composer-sa.email}"
  depends_on = [google_service_account.composer-sa]
}

resource "google_project_iam_member" "iam-service-account-user" {
  project    = var.project
  role       = "roles/iam.serviceAccountUser"
  member     = "serviceAccount:${google_service_account.composer-sa.email}"
  depends_on = [google_service_account.composer-sa]
}

resource "google_service_account_iam_binding" "composer-sa-iam" {
  service_account_id = google_service_account.composer-sa.name
  role               = "roles/composer.ServiceAgentV2Ext"
  members = [
    "serviceAccount:service-${var.project_number}@cloudcomposer-accounts.iam.gserviceaccount.com",
  ]

  depends_on = [google_service_account.composer-sa]
}
