# The Colonial - Exploring 157 years of Canadian Trademarks

On June 12, 1866, J.D. King & Co. registered the 
[first Trademark](https://ised-isde.canada.ca/cipo/trademark-search/0074366) 
in Canada to protect their design of "THE COLONIAL," their brand of Cuban 
cigars. Nearly 2 million trademark applications have been filed since then. 

The administration and processing of the majority of intellectual property in 
Canada is overseen by the Canadian Intellectual Property Office (CIPO). 
From 2022 to 2023 they received nearly 200 trademark applications per day.


## Overview

### Data Stack

This batch ELT pipeline is comprised of several GCP services for ingestion, 
transformation, and serving.

- Cloud Composer 2 (managed Airflow)
- Dataproc (managed Spark)
- Dataflow (templated data processing)
- Cloud Storage (data lake)
- BigQuery (data warehouse)
- Astronomer Cosmos (Airflow + dbt-core integration)
- dbt-core 1.7.10 (data modeling)
- Metabase (analytics)

### Files

| File | Description | Source |
| --- | --- | --- |
| `wipo_status_codes.txt` |  | |
| `party_type_codes.txt` |  | |
| `nice_classification_codes.txt` |  | |
| `TM_application_main_2023-09-12.csv` | Contains the basic information on the trademark application filed, including the primary key (`Application Number`). | [Download](https://opic-cipo.ca/cipo/client_downloads/Trademarks_ResearcherDataset_CSVTXT_Q2FY2023/TM_application_main_2023-09-12.zip) |
| `TM_interested_party_2023-09-12.csv` | Contains detailed information on the interested parties (Applicant, Registrant, Agent, etc.)| [Download](https://opic-cipo.ca/cipo/client_downloads/Trademarks_ResearcherDataset_CSVTXT_Q2FY2023/TM_application_main_2023-09-12.zip) |
| `TM_cipo_classification_2023-09-12.csv` | Contains the [Nice Classifications](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/trademarks/goods-and-services-manual-class-headings) of the Trademark. | [Download](https://opic-cipo.ca/cipo/client_downloads/Trademarks_ResearcherDataset_CSVTXT_Q2FY2023/TM_cipo_classification_2023-09-12.zip) |


## Instructions

### Before you begin

1. Have an active [Google Cloud Platform (GCP) account](https://console.cloud.google.com/freetrial) 
with billing enabled.
1. You've [installed Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli).
1. [gcloud CLI is installed](https://cloud.google.com/sdk/docs/install).

### GCP Setup

1. Create a new gcloud [named configuration](https://cloud.google.com/sdk/gcloud/reference/config/configurations/create) 
and activate it. Decide on a project name, which we will refer 
to as `PROJECT_ID` in later steps.
    ```shell copy
    gcloud config configuration create PROJECT_ID
    gcloud config configurations activate PROJECT_ID
    gcloud config set account YOUR_GCP_EMAIL
    ```
1. Create a new project using the `PROJECT_ID`.
    ```shell copy
    gcloud projects create PROJECT_ID
    gcloud config set project PROJECT_ID
    ```
    If a `WARNING` is returned, you may need to set the 
    [Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials) 
    quota project.

    ```shell copy
    gcloud auth application-default set-quota-project PROJECT_ID
    ```
1. Verify the new configuration is active with the expected project and account.
    ```shell copy
    gcloud config configurations list
    ```
1. Link a billing account to the project.️

    ***This command is in beta and might change without notice.*** Alternatively,
    you can enable the project's billing account using the Google Cloud Console 
    [web interface](https://cloud.google.com/billing/docs/how-to/modify-project#how-to-enable-billing).
    ```shell copy
     gcloud beta billing accounts list
     # Note the ACCOUNT_ID of the billing account you want to use
     gcloud beta billing projects link PROJECT_ID --billing-account ACCOUNT_ID
     ```
1. Create a new service account and make note of the `EMAIL`. This will be referred to as `SERVICE_ACCOUNT_EMAIL` in the next step.
    ```shell copy
    gcloud iam service-accounts create owner-sa --display-name="DELETE ME LATER"
    gcloud iam service-accounts list
    ```
1. Grant the `Owner` role to the service account. 

    *Note: granting basic roles in production environments is against 
    [best practices](https://cloud.google.com/iam/docs/best-practices-service-accounts), 
    so ensure that you follow the [teardown instructions]() to delete this afterwards.*

    ```shell copy
    gcloud projects add-iam-policy-binding PROJECT_ID \
        --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
        --role="roles/owner"
    ```
1. Confirm the `Owner` service account was successfully created. 
    ```shell copy
    gcloud iam service-accounts list
    ```
1. Generate a service account key (`owner-sa-key.json`) and save it to the `/keys` project directory. 
    ```shell copy
    # Run this from the root directory of the project
    gcloud iam service-accounts keys create \
        ./keys/owner-sa-key.json \
        --iam-account=SERVICE_ACCOUNT_EMAIL
    ```
1. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to the newly created service account key. Terraform will use this later to authenticate.
    ```shell copy
    export GOOGLE_APPLICATION_CREDENTIALS={{path_to_keyfile}}
    ```
1. Enable all the services required by the project.
    ```shell copy
    # This may take a minute to complete
    gcloud services enable \
        bigquery.googleapis.com \
        composer.googleapis.com \
        dataflow.googleapis.com \
        dataproc.googleapis.com \
        storage.googleapis.com \
        storage-component.googleapis.com
    ```

### Terraform Setup
Use the same `PROJECT_ID` from [GCP Setup]().
```hcl copy
project = "{{PROJECT_ID}}"
keyfile = "./keys/owner-sa-key.json"
```

```shell copy
terraform plan -var="project=<your-gcp-project-id>"
```

```shell copy
terraform apply -var="project=<your-gcp-project-id>"
```

### Teardown
1. Deprovision project related infrastructure.
    ```shell copy
    terraform destroy
    ```
1. Delete the `Owner` service account created in [GCP Setup]().

    ```shell copy
    gcloud iam service-accounts delete SERVICE_ACCOUNT_EMAIL
    ```

## See also

* https://ised-isde.canada.ca/cipo/trademark-search/srch?lang=eng
* https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/canadian-intellectual-property-statistics/trademarks-researcher-datasets-applications-and-registrations-csv-and-txt
* https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/trademarks-researcher-datasets-data-dictionary
