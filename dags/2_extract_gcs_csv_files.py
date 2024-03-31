import os
from airflow.datasets import Dataset
from airflow.decorators import dag
from airflow.providers.google.cloud.operators.dataflow import (
    DataflowTemplatedJobStartOperator,
)
from airflow.utils.dates import days_ago

PROJECT_ID = os.environ.get("PROJECT_ID")
REGION = os.environ.get("REGION")
BUCKET = os.environ.get("DATA_BUCKET")
BUCKET_PATH = f"gs://{BUCKET}"
APPLICATION_MAIN_FILENAME = "TM_application_main_2023-09-12.csv"
APPLICATION_MAIN_GCS = Dataset(f"{BUCKET_PATH}/raw/{APPLICATION_MAIN_FILENAME}")
INTERESTED_PARTY_FILENAME = "TM_interested_party_2023-09-12.csv"
INTERESTED_PARTY_GCS = Dataset(f"{BUCKET_PATH}/raw/{INTERESTED_PARTY_FILENAME}")
CIPO_CLASSIFICATION_FILENAME = "TM_cipo_classification_2023-09-12.csv"
CIPO_CLASSIFICATION_GCS = Dataset(f"{BUCKET_PATH}/raw/{CIPO_CLASSIFICATION_FILENAME}")
OPPOSITION_CASE_FILENAME = "TM_opposition_case_2023-09-12.csv"
OPPOSITION_CASE_GCS = Dataset(f"{BUCKET_PATH}/raw/{OPPOSITION_CASE_FILENAME}")


@dag(
    "extract_gcs_zip_files",
    start_date=days_ago(1),
    schedule=None,
    catchup=False,
    description="Bulk extracts all ZIP files files from the raw/compressed folder.",
)
def extract_gcs_zip_files():
    start_template_job = DataflowTemplatedJobStartOperator(
        task_id="bulk-unzip",
        project_id=PROJECT_ID,
        location=REGION,
        template="gs://dataflow-templates/latest/Bulk_Decompress_GCS_Files",
        parameters={
            "inputFilePattern": f"{BUCKET_PATH}/raw/compressed/*.zip",
            "outputDirectory": f"{BUCKET_PATH}/raw",
            "outputFailureFile": f"{BUCKET_PATH}/raw/logs/failed.csv",
        },
        outlets=[
            APPLICATION_MAIN_GCS,
            INTERESTED_PARTY_GCS,
            CIPO_CLASSIFICATION_GCS,
            OPPOSITION_CASE_GCS,
        ],
    )

    start_template_job


extract_gcs_zip_files()
