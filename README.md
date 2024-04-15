# Exploring 158 Years of Canadian Trademark Data

![preview](/assets/preview.jpg)
[View interactive dashboard](https://lookerstudio.google.com/s/keWPSnG8YgA)

## Overview
The [oldest trademark](https://ised-isde.canada.ca/cipo/trademark-search/0042293)
ever registered in Canada, according to public records from the Canadian 
Intellectual Property Office (CIPO), is the word trademark 'IMPERIAL,' owned by 
Unilever Canada Inc. and registered on July 29, 1865, for a brand of soap. 
On a quarterly basis, the CIPO releases 
[trademark researcher datasets](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/canadian-intellectual-property-statistics/trademarks-researcher-datasets-applications-and-registrations-csv-and-txt) 
containing records of trademark applications and registrations. 

This project explores a subset of these datasets by processing trademark data 
from 1865 to 2023 and visualizing them as:

  - Registered trademarks by category over decades and years.
  - Trademarks applications and registrations over decades and years.
  - Trademarks registered versus disputed by ranking and interested party.


### Data Stack

This batch ELT pipeline is comprised of several Google Cloud Platform (GCP) 
services for ingestion, transformation, and serving. The data pipeline 
orchestrated by Cloud Composer 2 (managed Airflow) utilizes 
[datasets](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/datasets.html) 
in each DAG to enable fully automated data-aware scheduling. The source CSV 
files containing 13 million records are automatically downloaded to the Cloud 
Storage data lake for processing. Dataflow decompresses the files while Spark 
jobs apply a schema and transform each file into Parquet format where they are 
then loaded into the data warehouse.  The BigQuery tables are partitioned and 
clustered before transformations are applied in dbt. With Cosmos, the entire dbt 
project is encapsulated within an Airflow task group, enhancing transparency of 
the dbt data lineage graph and providing finer-grained control over the model 
materialization process. The visualizations in Looker Studio feature 
cross-filtering, data drilling (on decade/year), and controls for interactive 
analysis.

- Cloud Composer 2.6.6 (Airflow 2.7.3)
- Dataproc (managed Spark)
- BigQuery
- Dataflow
- Cloud Storage
- dbt-core
- Cosmos
- Looker Studio


### Datasets

| File | Description | Records | Source |
| --- | --- | --- | --- |
| TM_application_main_2024-03-06.csv | Contains basic information about the trademark application filed, including the primary key (`Application Number`). | 1,971,623 | [Download](https://opic-cipo.ca/cipo/client_downloads/TM_CSV_2024_03_07/TM_application_main_2024-03-06.zip) |
| TM_interested_party_2024-03-06.csv | Contains detailed information about the interested parties (Applicant, Registrant, Agent, etc.)| 4,604,423 | [Download](https://opic-cipo.ca/cipo/client_downloads/TM_CSV_2024_03_07/TM_interested_party_2024-03-06.zip) |
| TM_cipo_classification_2024-03-06.csv | Contains the [Nice Classifications](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/trademarks/goods-and-services-manual-class-headings) of the Trademark. | 6,262,267 | [Download](https://opic-cipo.ca/cipo/client_downloads/TM_CSV_2024_03_07/TM_cipo_classification_2024-03-06.zip) |
| TM_opposition_case_2024-03-06.zip | Contains information on the opposition case, including details of the plaintiff and defendant. | 40,216 | [Download](https://opic-cipo.ca/cipo/client_downloads/TM_CSV_2024_03_07/TM_opposition_case_2024-03-06.zip) |
| cipo_status_codes.csv | Mapping of CIPO status code IDs and descriptions. | 42 | [Link](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/trademarks-researcher-datasets-data-dictionary) |
| wipo_status_codes.csv | Mapping of WIPO (World Intellectual Property Organization) status code IDs and descriptions. | 17 | [Link](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/trademarks-researcher-datasets-data-dictionary) |
| party_type_codes.csv | Mapping of party type code IDs and descriptions. | 7 | [Link](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/trademarks-researcher-datasets-data-dictionary) |
| nice_classification_codes.csv | Mapping of Nice classification of goods and service IDs and descriptions.  | 46 | [Link](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/trademarks-researcher-datasets-data-dictionary) |


## Instructions

### ✅ Before you begin

1. Have an active [GCP account](https://console.cloud.google.com/freetrial) 
with billing enabled.
1. You've [installed Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli).
1. [gcloud CLI is installed](https://cloud.google.com/sdk/docs/install).


### ⚙️ GCP Setup

1. Decide on a project name and set it as the `$PROJECT_ID` environment variable.
    ```shell copy
    export PROJECT_ID={{YOUR_PROJECT_NAME}}
    echo $PROJECT_ID
    ```
1. Create a new gcloud [named configuration](https://cloud.google.com/sdk/gcloud/reference/config/configurations/create) 
and activate it. 
    ```shell copy
    gcloud config configuration create $PROJECT_ID
    gcloud config configurations activate $PROJECT_ID
    gcloud config set account YOUR_GCP_EMAIL
    ```
1. Create a new project.
    ```shell copy
    gcloud projects create $PROJECT_ID
    gcloud config set project $PROJECT_ID
    ```
    If a `WARNING` is returned, you may need to set the 
    [Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials) 
    quota project.

    ```shell copy
    gcloud auth application-default set-quota-project $PROJECT_ID
    ```
1. Verify the new configuration is active with the expected project and account.
    ```shell copy
    gcloud config configurations list
    ```
1. Link a billing account to the project.️ To see a list of your billing accounts, run:
    ```shell copy
    # This command is in beta and might change without notice!
    gcloud beta billing accounts list
    ```

    Make note of the `ACCOUNT_ID` of the billing account you want to use from the returned output and link the project to it.
    ```shell copy
    gcloud beta billing projects link $PROJECT_ID --billing-account ACCOUNT_ID
    ```
1. Create a new service account.
    ```shell copy
    gcloud iam service-accounts create owner-sa --display-name="DELETE ME LATER"
    ```
1. Grant the `Owner` role to the service account. 

    *Note: granting basic roles in production environments is against 
    [best practices](https://cloud.google.com/iam/docs/best-practices-service-accounts), 
    so ensure that you follow the [teardown instructions]() to delete this 
    afterwards.*

    ```shell copy
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:owner-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/owner"
    ```
1. Confirm the `Owner` service account was successfully created and that it has
  the the owner basic role assigned.
    ```shell copy
    gcloud iam service-accounts list
    gcloud projects get-iam-policy $PROJECT_ID \
        --flatten="bindings[].members" \
        --format='table(bindings.role)' \
        --filter="bindings.members:owner-sa@${PROJECT_ID}.iam.gserviceaccount.com"
    ```
1. Generate a service account key (`owner-sa-key.json`) and save it to the 
`/keys` project directory. 
    ```shell copy
    # Run this from the root directory of the project
    gcloud iam service-accounts keys create \
        ./keys/owner-sa-key.json \
        --iam-account=owner-sa@$PROJECT_ID.iam.gserviceaccount.com
    ```
1. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to the 
newly created service account key. Terraform will use this later to authenticate.
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


### 🌱 Terraform Setup

1. Create a new file called `terraform.tfvars` in the `/terraform` project 
    directory using this template:
    ```hcl copy
    project = "{{PROJECT_ID}}"
    project_number = "{{PROJECT_NUMBER}}"
    keyfile = "../keys/owner-sa-key.json"
    ```

    You can find your `PROJECT_NUMBER` by running:
    ```shell copy
    gcloud projects list \
        --filter="$(gcloud config get-value project)" \
        --format="value(PROJECT_NUMBER)"
    ```
1. Initialize Terraform and review the infrastructure change plan.
    ```shell copy
    terraform init
    terraform plan
    ```
1. Begin provisioning infrastructure. It can take 25+ minutes for this step to 
    complete and an additional few minutes for Cloud Composer to load all the DAGs.
    ```shell copy
    terraform apply
    ```

### dbt Setup

1. Update the *`project`* attribute with the name of your `PROJECT_ID` in 
[`profiles.yml`](/dags/dbt/ca_trademarks_dp/profiles.yml#L6) to complete the 
`dbt-bigquery` connector setup.
1. Upload the updated `profiles.yml` to the dbt project folder.
    ```shell copy
    # Run this from the root directory of the project
    gcloud composer environments storage dags import \
        --source='dags/dbt/ca_trademarks_dp/profiles.yml' \
        --destination='dbt/ca_trademarks_dp/' \
        --environment='ca-trademarks-composer2' \
        --location='us-west1'
    ```

### 🚀 Initialize Airflow DAGs

1. Generate a service account key (`composer-sa-key.json`) for the Cloud Composer
  service account created by the Terraform script and save it to the `/keys` 
  project directory. 
    ```shell copy
    # Run this from the root directory of the project
    gcloud iam service-accounts keys create \
        ./keys/composer-sa-key.json \
        --iam-account=composer-env-account@${PROJECT_ID}.iam.gserviceaccount.com

    # Note the KEY_ID of the key that was just created.
    gcloud iam service-accounts keys list \
        --iam-account=composer-env-account@${PROJECT_ID}.iam.gserviceaccount.com
    ```
1. Download the keyfile locally and upload it to the dbt folder.
    ```shell copy
    # Run this from the root directory of the project
    gcloud beta iam service-accounts keys get-public-key <KEY_ID> \
        --iam-account=composer-env-account@${PROJECT_ID}.iam.gserviceaccount.com \
        --output-file=./keys/composer-sa-key.json

    # Upload keyfile to dbt project folder
    gcloud composer environments storage dags import \
        --source='keys/composer-sa-key.json' \
        --destination='dbt/ca_trademarks_dp/' \
        --environment='ca-trademarks-composer2' \
        --location='us-west1'
    ```
1. Navigate to your [Cloud Composer environments](https://console.cloud.google.com/composer/environments) 
on Google Cloud console.
1. In the Airflow webserver column, follow the link to access the Airflow UI.
1. To initialize the data pipeline, start the ***upload_raw_trademark_files_to_gcs*** 
DAG by activating the ▶️ (Trigger DAG) button under the **Actions** column. 
Subsequent DAGs will be automatically triggered upon successful completion of 
upstream DAGs. Execution of the entire pipeline can take over 20 minutes.
1. Progress of each DAG can be monitored from the 
[Airflow UI](https://airflow.apache.org/docs/apache-airflow/stable/ui.html).

> [!IMPORTANT]
> The `dbt` DAG is a task group composed of 16 tasks and dependencies. Depending
> on resource availability, you may be required to
[manually rerun them.](https://docs.astronomer.io/learn/rerunning-dags#manually-rerun-tasks-or-dags)


### 💥 Teardown

1. Deprovision project related infrastructure. This will take ~6 minutes.
    ```shell copy
    cd terraform/
    terraform destroy
    ```
1. Delete project related service accounts.
    ```shell copy
    # Owner SA
    gcloud iam service-accounts delete owner-sa@$PROJECT_ID.iam.gserviceaccount.com 
    ```
1. [Delete](https://cloud.google.com/storage/docs/deleting-buckets#delete-bucket-console) 
any additional staging buckets created by Dataflow and Dataproc.
    ```shell copy
    gsutil ls
    gsutil -m rm -r <bucket_to_remove>
    ```

## See also

* https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/trademarks-researcher-datasets-data-dictionary
