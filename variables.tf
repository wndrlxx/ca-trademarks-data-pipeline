variable "project" {}
variable "project_number" {}
variable "keyfile" {}

variable "location" {
  default = "US"
}

variable "region" {
  default = "us-west1"
}

variable "zone" {
  default = "us-west1-a"
}

variable "data_bucket_name" {
  default = "ca-trademarks-2023-09-12"
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