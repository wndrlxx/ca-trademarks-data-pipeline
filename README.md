# Exploring 158 Years of Canadian Trademark Data

![preview](/assets/preview.jpg)
> [View interactive dashboard](https://lookerstudio.google.com/s/keWPSnG8YgA)

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

![dbt lineage graph as Airflow task group](/assets/lineage_graph.png)
> *dbt lineage graph as Airflow task group*

### Datasets

| File | Description | Records | Source |
| --- | --- | --- | --- |
| TM_application_main_2024-03-06.csv | Contains basic information about the trademark application filed, including the primary key (`Application Number`). | 1,971,623 | [Download](https://opic-cipo.ca/cipo/client_downloads/TM_CSV_2024_03_07/TM_application_main_2024-03-06.zip) |
| TM_interested_party_2024-03-06.csv | Contains detailed information about the interested parties (Applicant, Registrant, Agent, etc.)| 4,604,423 | [Download](https://opic-cipo.ca/cipo/client_downloads/TM_CSV_2024_03_07/TM_interested_party_2024-03-06.zip) |
| TM_cipo_classification_2024-03-06.csv | Contains the [Nice Classifications](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/trademarks/goods-and-services-manual-class-headings) of the Trademark. | 6,262,267 | [Download](https://opic-cipo.ca/cipo/client_downloads/TM_CSV_2024_03_07/TM_cipo_classification_2024-03-06.zip) |
| TM_opposition_case_2024-03-06.csv | Contains information on the opposition case, including details of the plaintiff and defendant. | 40,216 | [Download](https://opic-cipo.ca/cipo/client_downloads/TM_CSV_2024_03_07/TM_opposition_case_2024-03-06.zip) |
| cipo_status_codes.csv | Mapping of CIPO status code IDs and descriptions. | 42 | [Link](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/trademarks-researcher-datasets-data-dictionary) |
| wipo_status_codes.csv | Mapping of WIPO (World Intellectual Property Organization) status code IDs and descriptions. | 17 | [Link](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/trademarks-researcher-datasets-data-dictionary) |
| party_type_codes.csv | Mapping of party type code IDs and descriptions. | 7 | [Link](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/trademarks-researcher-datasets-data-dictionary) |
| nice_classification_codes.csv | Mapping of Nice classification of goods and service IDs and descriptions.  | 46 | [Link](https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/trademarks-researcher-datasets-data-dictionary) |


## Instructions

> [!NOTE]
> These instructions have only been tested on macOS. YMMV on other platforms.

### ✅ Before you begin

1. Have an active [GCP account](https://console.cloud.google.com/freetrial) 
with billing enabled.
1. You've [installed Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli).
1. [gcloud CLI is installed](https://cloud.google.com/sdk/docs/install).
    ```shell copy
    # macOS install using Homebrew
    brew install --cask google-cloud-sdk
    ```
1. You have GNU Make 3.81 or newer installed.

### 🌱 Set environment variables

1. Decide on a project name and set it as the `$PROJECT_ID` environment variable.
    ```shell copy
    export PROJECT_ID={{YOUR_PROJECT_NAME}}
    ```
1. Set the `$GCP_EMAIL` environment variable to the email associated with your 
    active GCP account.
    ```shell copy
    export GCP_EMAIL={{YOUR_GCP_EMAIL}}
    ```
1. Set the `$BILLING_ACCOUNT_ID` environment variable to the value of the 
    `ACCOUNT_ID` returned by `gcloud billing accounts list` that you wish to 
    link to this Google Cloud project. 
    ```shell copy
    export BILLING_ACCOUNT_ID={{ACCOUNT_ID}}
    ```
1. Set `$GCP_REGION` to your desired 
[GCP region](https://cloud.google.com/compute/docs/regions-zones#available).
    ```shell copy
    export GCP_REGION={{REGION}}
    ```

### 🔧 Make install

*Run the following commands from the root project directory.*

1. Verify the environment variables are correctly set.
    ```shell copy
    make env-test
    ```
1. Initialize a new GCP project and service account.
    ```shell copy
    make gcp-up
    ```
1. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the absolute 
path of the service account key. Terraform will need this to authenticate.
    ```shell copy
    export GOOGLE_APPLICATION_CREDENTIALS={{full_path_to_keyfile}}
    ```
    On macOS:
    ```shell copy
    export GOOGLE_APPLICATION_CREDENTIALS=$(realpath keys/owner-sa-key.json)
    ```
1. Enable all the Google APIs required by the project.
    ```shell copy
    make enable-gcp-services
    ```
1. Provision infrastructure. Type `yes` to approve actions. 
    *This step can take 40+ minutes to complete.*
    ```shell copy
    make -f tf.Makefile up
    ```

    *If this step fails, you can try running:*
    ```shell copy
    make -f tf.Makefile retry
    ```
1. Complete dbt-core setup.
    ```shell copy
    make dbt-setup
    ```

### 🚀 Initialize Airflow DAGs

1. Navigate to your 
[Cloud Composer environments](https://console.cloud.google.com/composer/environments) 
on Google Cloud console.
1. In the Airflow webserver column, follow the link to access the Airflow UI.
1. To initialize the data pipeline, start the ***upload_raw_trademark_files_to_gcs*** 
DAG by activating the ▶️ (Trigger DAG) button under the **Actions** column. 
Subsequent DAGs will be automatically triggered upon successful completion of 
upstream DAGs. Execution of the entire pipeline can take over 20 minutes.
1. Progress of each DAG can be monitored from the 
[Airflow UI](https://airflow.apache.org/docs/apache-airflow/stable/ui.html).

![dag runs](/assets/dag_runs.png)

> [!IMPORTANT]
> The `dbt` DAG is a task group composed of 20 tasks and dependencies. Depending
> on resource availability, you may be required to
[manually rerun them.](https://docs.astronomer.io/learn/rerunning-dags#manually-rerun-tasks-or-dags)


### 💥 Teardown

1. Deprovision project related infrastructure. Type `yes` to approve actions.
    ```shell copy
    make -f tf.Makefile down
    ```
1. Delete the GCP project. Type `Y` to confirm.
    ```shell copy
    make gcp-down
    ```

## See also

* https://ised-isde.canada.ca/site/canadian-intellectual-property-office/en/trademarks-researcher-datasets-data-dictionary
