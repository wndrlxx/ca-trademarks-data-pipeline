ifndef PROJECT_ID
$(error PROJECT_ID environment variable is not set. Please set it and try again.)
endif

ifndef GCP_REGION
$(error GCP_REGION environment variable is not set. Please set it and try again.)
endif

ifndef BILLING_ACCOUNT_ID
$(error BILLING_ACCOUNT_ID environment variable is not set. Please set it and try again.)
endif

PROJECT_NUMBER := $(shell gcloud projects list \
	--filter="$$(gcloud config get-value project)" \
	--format="value(PROJECT_NUMBER)")

retry:
	terraform -chdir=./terraform apply \
	-var "project=${PROJECT_ID}" \
	-var "region=${GCP_REGION}" \
	-var "project_number=${PROJECT_NUMBER}"

up:
	terraform -chdir=./terraform init
	make -f $(firstword $(MAKEFILE_LIST)) retry

down:
	terraform -chdir=./terraform destroy \
	-var "project=${PROJECT_ID}" \
	-var "region=${GCP_REGION}" \
	-var "project_number=${PROJECT_NUMBER}"