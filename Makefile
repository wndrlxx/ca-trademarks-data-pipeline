ifndef PROJECT_ID
$(error PROJECT_ID environment variable is not set. Please set it and try again.)
endif

ifndef GCP_REGION
$(error GCP_REGION environment variable is not set. Please set it and try again.)
endif

ifndef GCP_EMAIL
$(error GCP_EMAIL environment variable is not set. Please set it and try again.)
endif

ifndef BILLING_ACCOUNT_ID
$(error BILLING_ACCOUNT_ID environment variable is not set. Please set it and try again.)
endif

env-test:
	@echo PROJECT_ID = ${PROJECT_ID}
	@echo GCP_REGION = ${GCP_REGION}
	@echo GCP_EMAIL = ${GCP_EMAIL}
	@echo BILLING_ACCOUNT_ID = ${BILLING_ACCOUNT_ID}

gcp-up: gcloud-config gcloud-new-project create-owner-sa-and-key

gcloud-config:
	@echo ====== Creating new gcloud named configuration...
	gcloud config configurations create ${PROJECT_ID}
	gcloud config configurations activate ${PROJECT_ID}
	gcloud config set account ${GCP_EMAIL}

gcloud-new-project:
	@echo ====== Creating new Google Cloud project...
	gcloud projects create ${PROJECT_ID}
	gcloud config set project ${PROJECT_ID}
	gcloud auth application-default set-quota-project ${PROJECT_ID}
	@echo ====== Linking billing account to project...
	gcloud billing projects link ${PROJECT_ID} --billing-account ${BILLING_ACCOUNT_ID}

create-owner-sa-and-key:
	@echo ====== Creating owner service account...
	gcloud iam service-accounts create owner-sa --display-name="DELETE ME LATER"
	gcloud projects add-iam-policy-binding ${PROJECT_ID} \
		--member="serviceAccount:owner-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
		--role="roles/owner"
	@echo ====== Creating service account key...
	gcloud iam service-accounts keys create \
		./keys/owner-sa-key.json \
		--iam-account=owner-sa@${PROJECT_ID}.iam.gserviceaccount.com

enable-gcp-services:
	@echo ====== Enabling GCP APIs...
	gcloud services enable \
		bigquery.googleapis.com \
		composer.googleapis.com \
		dataflow.googleapis.com \
		dataproc.googleapis.com \
		storage.googleapis.com \
		storage-component.googleapis.com

composer-up: create-composer-key upload-composer-key

create-composer-key:
	@echo ====== Creating Composer service account key...
	gcloud iam service-accounts keys create \
		./keys/composer-sa-key.json \
		--iam-account=composer-env-account@${PROJECT_ID}.iam.gserviceaccount.com

upload-composer-key:
	@echo ====== Uploading service account key...
	gcloud composer environments storage dags import \
		--source='keys/composer-sa-key.json' \
		--destination='dbt/ca_trademarks_dp/' \
		--environment='ca-trademarks-composer2' \
		--location=${GCP_REGION}

dbt-setup:
	@echo ====== Starting dbt setup...
	./setup.sh
	gcloud composer environments storage dags import \
		--source='dags/dbt/ca_trademarks_dp/profiles.yml' \
		--destination='dbt/ca_trademarks_dp/' \
		--environment='ca-trademarks-composer2' \
		--location=${GCP_REGION}
	composer-up
	@echo ====== Completed dbt setup!

delete-owner-sa:
	@echo ====== Deleting owner service account...
	gcloud iam service-accounts delete owner-sa@${PROJECT_ID}.iam.gserviceaccount.com 