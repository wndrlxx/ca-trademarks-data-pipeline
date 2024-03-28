variable "project" {}

variable "keyfile" {}

variable "region" {
  default = "us-west1"
}

variable "location" {
  default = "US"
}

variable "bq_dataset_name" {
  default = "ca_trademarks"
}

variable "gcs_bucket_name" {
  default = "ca-trademarks-2023-09-12"
}
