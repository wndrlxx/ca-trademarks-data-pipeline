import os
import requests
from google.cloud import storage
from airflow.datasets import Dataset
from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from include.ca_trademark_files import (
    TmApplicationMainFile,
    TmInterestedPartyFile,
    TmCipoClassificationFile,
    TmOppositionCaseFile,
)

DATA_BUCKET_NAME = os.environ.get("DATA_BUCKET", "ca-trademarks-2024-03-06")
application_main = TmApplicationMainFile(DATA_BUCKET_NAME)
interested_party = TmInterestedPartyFile(DATA_BUCKET_NAME)
cipo_classification = TmCipoClassificationFile(DATA_BUCKET_NAME)
opposition_case = TmOppositionCaseFile(DATA_BUCKET_NAME)

# ZIP Datasets
APPLICATION_MAIN_ZIP = Dataset(application_main.csv_zip_filepath())
INTERESTED_PARTY_ZIP = Dataset(interested_party.csv_zip_filepath())
CIPO_CLASSIFICATION_ZIP = Dataset(cipo_classification.csv_zip_filepath())
OPPOSITION_CASE_ZIP = Dataset(opposition_case.csv_zip_filepath())


def upload_file_to_gcs(
    url: str,
    csv_zip_filename: str,
):
    # NOTE: SSLError is raised if verify=False is not specified
    response = requests.get(url, verify=False, stream=True)
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(DATA_BUCKET_NAME)
    blob = bucket.blob(f"raw/compressed/{csv_zip_filename}")
    blob.upload_from_string(response.content, content_type="application/zip")


@dag(
    "upload_raw_trademark_files_to_gcs",
    description="""Download the raw, compressed data from the CIPO trademarks 
                researcher dataset website.""",
    start_date=days_ago(1),
    schedule=None,
    catchup=False,
)
def download_tm_files_to_gcs():
    @task
    def begin():
        print("Starting tasks...")

    @task(outlets=[APPLICATION_MAIN_ZIP])
    def upload_application_main_file():
        upload_file_to_gcs(
            url=application_main.source_url(),
            csv_zip_filename=application_main.csv_zip_filename(),
        )

    @task(outlets=[INTERESTED_PARTY_ZIP])
    def upload_interested_party_file():
        upload_file_to_gcs(
            url=interested_party.source_url(),
            csv_zip_filename=interested_party.csv_zip_filename(),
        )

    @task(outlets=[CIPO_CLASSIFICATION_ZIP])
    def upload_cipo_classification_file():
        upload_file_to_gcs(
            url=cipo_classification.source_url(),
            csv_zip_filename=cipo_classification.csv_zip_filename(),
        )

    @task(outlets=[OPPOSITION_CASE_ZIP])
    def upload_opposition_case_file():
        upload_file_to_gcs(
            url=opposition_case.source_url(),
            csv_zip_filename=opposition_case.csv_zip_filename(),
        )

    begin() >> [
        upload_application_main_file(),
        upload_interested_party_file(),
        upload_cipo_classification_file(),
        upload_opposition_case_file(),
    ]


download_tm_files_to_gcs()
