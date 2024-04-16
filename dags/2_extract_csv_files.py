import os
from airflow.datasets import Dataset
from airflow.decorators import dag
from airflow.providers.google.cloud.operators.dataflow import (
    DataflowTemplatedJobStartOperator,
)
from airflow.utils.dates import days_ago
from include.ca_trademark_files import (
    TmApplicationMainFile,
    TmInterestedPartyFile,
    TmCipoClassificationFile,
    TmOppositionCaseFile,
)

PROJECT_ID = os.environ.get("PROJECT", "ca-tm-dp")
REGION = os.environ.get("REGION", "us-west1")
DATA_BUCKET_NAME = os.environ.get("DATA_BUCKET", "ca-trademarks-2024-03-06")
BUCKET_PATH = f"gs://{DATA_BUCKET_NAME}"

application_main = TmApplicationMainFile(DATA_BUCKET_NAME)
interested_party = TmInterestedPartyFile(DATA_BUCKET_NAME)
cipo_classification = TmCipoClassificationFile(DATA_BUCKET_NAME)
opposition_case = TmOppositionCaseFile(DATA_BUCKET_NAME)


@dag(
    "extract_zip_files",
    description="Bulk extracts all ZIP files from the raw/compressed folder.",
    start_date=days_ago(1),
    catchup=False,
    schedule=[
        Dataset(application_main.csv_zip_filepath()),
        Dataset(interested_party.csv_zip_filepath()),
        Dataset(cipo_classification.csv_zip_filepath()),
        Dataset(opposition_case.csv_zip_filepath()),
    ],
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
            "outputFailureFile": f"{BUCKET_PATH}/logs/failed.csv",
        },
        outlets=[
            Dataset(application_main.csv_filepath()),
            Dataset(interested_party.csv_filepath()),
            Dataset(cipo_classification.csv_filepath()),
            Dataset(opposition_case.csv_filepath()),
        ],
    )

    start_template_job


extract_gcs_zip_files()
