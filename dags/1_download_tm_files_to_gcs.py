import os
import requests
from google.cloud import storage
from airflow.utils.dates import days_ago
from airflow.datasets import Dataset
from airflow.decorators import dag, task

BUCKET = os.environ.get("DATA_BUCKET")
BUCKET_PATH = f"gs://{BUCKET}"
RAW_DATA_PATH = f"{BUCKET_PATH}/raw"
COMPRESSED_DATA_PATH = f"{RAW_DATA_PATH}/compressed"
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
CIPO_URL = "https://opic-cipo.ca/cipo/client_downloads/Trademarks_ResearcherDataset_CSVTXT_Q2FY2023"


@dag(
    "upload_raw_trademark_files_to_gcs",
    start_date=days_ago(1),
    schedule=None,
    catchup=False,
    description="""Download the raw, compressed data from the CIPO trademarks researcher dataset 
                website.""",
)
def download_tm_files_to_gcs():
    @task(outlets=[APPLICATION_MAIN_ZIP_GCS])
    def upload_application_main_file():
        url = f"{CIPO_URL}/{APPLICATION_MAIN_ZIP_FILENAME}"

        # NOTE: SSLError is raised if verify=False is not specified
        response = requests.get(url, verify=False, stream=True)
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(BUCKET)
        blob = bucket.blob(f"raw/compressed/{APPLICATION_MAIN_ZIP_FILENAME}")
        blob.upload_from_string(response.content, content_type="application/zip")

    @task(outlets=[INTERESTED_PARTY_ZIP_GCS])
    def upload_interested_party_file():
        url = f"{CIPO_URL}/{INTERESTED_PARTY_ZIP_FILENAME}"

        # NOTE: SSLError is raised if verify=False is not specified
        response = requests.get(url, verify=False, stream=True)
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(BUCKET)
        blob = bucket.blob(f"raw/compressed/{INTERESTED_PARTY_ZIP_FILENAME}")
        blob.upload_from_string(response.content, content_type="application/zip")

    @task(outlets=[CIPO_CLASSIFICATION_ZIP_GCS])
    def upload_cipo_classification_file():
        url = f"{CIPO_URL}/{CIPO_CLASSIFICATION_ZIP_FILENAME}"

        # NOTE: SSLError is raised if verify=False is not specified
        response = requests.get(url, verify=False, stream=True)
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(BUCKET)
        blob = bucket.blob(f"raw/compressed/{CIPO_CLASSIFICATION_ZIP_FILENAME}")
        blob.upload_from_string(response.content, content_type="application/zip")

    @task(outlets=[OPPOSITION_CASE_ZIP_GCS])
    def upload_opposition_case_file():
        url = f"{CIPO_URL}/{OPPOSITION_CASE_ZIP_FILENAME}"

        # NOTE: SSLError is raised if verify=False is not specified
        response = requests.get(url, verify=False, stream=True)
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(BUCKET)
        blob = bucket.blob(f"raw/compressed/{OPPOSITION_CASE_ZIP_FILENAME}")
        blob.upload_from_string(response.content, content_type="application/zip")

    upload_application_main_file()
    upload_interested_party_file()
    upload_cipo_classification_file()
    upload_opposition_case_file()


download_tm_files_to_gcs()
