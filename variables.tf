variable "project" {}

variable "keyfile" {}

variable "owner_service_account" {}

variable "region" {
  default = "us-west1"
}

variable "zone" {
  default = "us-west1-a"
}

variable "location" {
  default = "US"
}

variable "bq_dataset_name" {
  default = "ca_trademarks"
}

variable "composer_env_name" {
  default = "ca-trademarks-composer2"
}

variable "composer_bucket_name" {
  default = "ca-trademarks-composer2"
}

variable "spark_staging_bucket_name" {
  default = "ca-trademarks-spark-staging"
}

variable "data_bucket_name" {
  default = "ca-trademarks-2023-09-12"
}
