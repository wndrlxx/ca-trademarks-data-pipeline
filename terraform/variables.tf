variable "project" {}
variable "project_number" {}
variable "region" {}

variable "keyfile" {
  default = "../keys/owner-sa-key.json"
}

variable "data_bucket_name" {
  default = "ca-trademarks-2024-03-06"
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