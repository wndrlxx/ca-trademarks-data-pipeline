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
RAW_DATA_PATH = f"{BUCKET_PATH}/raw"
COMPRESSED_DATA_PATH = f"{RAW_DATA_PATH}/compressed"

# CSV files
APPLICATION_MAIN_CSV_FILENAME = "TM_application_main_2023-09-12.csv"
INTERESTED_PARTY_CSV_FILENAME = "TM_interested_party_2023-09-12.csv"
CIPO_CLASSIFICATION_CSV_FILENAME = "TM_cipo_classification_2023-09-12.csv"
OPPOSITION_CASE_CSV_FILENAME = "TM_opposition_case_2023-09-12.csv"
# CSV Datasets
APPLICATION_MAIN_CSV_GCS = Dataset(f"{RAW_DATA_PATH}/{APPLICATION_MAIN_CSV_FILENAME}")
INTERESTED_PARTY_CSV_GCS = Dataset(f"{RAW_DATA_PATH}/{INTERESTED_PARTY_CSV_FILENAME}")
CIPO_CLASSIFICATION_CSV_GCS = Dataset(f"{RAW_DATA_PATH}/{CIPO_CLASSIFICATION_CSV_FILENAME}")
OPPOSITION_CASE_CSV_GCS = Dataset(f"{RAW_DATA_PATH}/{OPPOSITION_CASE_CSV_FILENAME}")
# ZIP files
APPLICATION_MAIN_ZIP_FILENAME = "TM_application_main_2023-09-12.zip"
INTERESTED_PARTY_ZIP_FILENAME = "TM_interested_party_2023-09-12.zip"
CIPO_CLASSIFICATION_ZIP_FILENAME = "TM_cipo_classification_2023-09-12.zip"
OPPOSITION_CASE_ZIP_FILENAME = "TM_opposition_case_2023-09-12.zip"
# ZIP Datasets
APPLICATION_MAIN_ZIP_GCS = Dataset(f"{COMPRESSED_DATA_PATH}/{APPLICATION_MAIN_ZIP_FILENAME}")
INTERESTED_PARTY_ZIP_GCS = Dataset(f"{COMPRESSED_DATA_PATH}/{INTERESTED_PARTY_ZIP_FILENAME}")
CIPO_CLASSIFICATION_ZIP_GCS = Dataset(f"{COMPRESSED_DATA_PATH}/{CIPO_CLASSIFICATION_ZIP_FILENAME}")
OPPOSITION_CASE_ZIP_GCS = Dataset(f"{COMPRESSED_DATA_PATH}/{OPPOSITION_CASE_ZIP_FILENAME}")


@dag(
    "extract_gcs_zip_files",
    start_date=days_ago(1),
    schedule=[
        APPLICATION_MAIN_ZIP_GCS,
        INTERESTED_PARTY_ZIP_GCS,
        CIPO_CLASSIFICATION_ZIP_GCS,
        OPPOSITION_CASE_ZIP_GCS,
    ],
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
            APPLICATION_MAIN_CSV_GCS,
            INTERESTED_PARTY_CSV_GCS,
            CIPO_CLASSIFICATION_CSV_GCS,
            OPPOSITION_CASE_CSV_GCS,
        ],
    )

    start_template_job


extract_gcs_zip_files()
