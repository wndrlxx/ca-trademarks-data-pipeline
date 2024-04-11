import os
from airflow import DAG
from airflow.datasets import Dataset
from airflow.operators.empty import EmptyOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import (
    GCSToBigQueryOperator,
)
from airflow.utils.dates import days_ago
from include.ca_trademark_files import (
    TmApplicationMainFile,
    TmInterestedPartyFile,
    TmCipoClassificationFile,
    TmOppositionCaseFile,
)

DATASET_NAME = os.environ.get("BQ_DATASET", "ca_trademarks")
DATA_BUCKET_NAME = os.environ.get("DATA_BUCKET", "ca-trademarks-2024-03-06")
application_main = TmApplicationMainFile(DATA_BUCKET_NAME)
interested_party = TmInterestedPartyFile(DATA_BUCKET_NAME)
cipo_classification = TmCipoClassificationFile(DATA_BUCKET_NAME)
opposition_case = TmOppositionCaseFile(DATA_BUCKET_NAME)


def create_external_table(tm_file):
    return GCSToBigQueryOperator(
        task_id=f"bq_create_{tm_file.filename}_external_table",
        bucket=f"{DATA_BUCKET_NAME}",
        source_format="PARQUET",
        source_objects=[f"transformed/{tm_file.parquet_filename()}/*.parquet"],
        destination_project_dataset_table=f"{DATASET_NAME}.external_{tm_file.table_id}",
        write_disposition="WRITE_TRUNCATE",
        external_table=True,
        autodetect=True,
        deferrable=True,
        outlets=[Dataset(tm_file.bigquery_external_table_fqn())],
    )


with DAG(
    dag_id="bigquery-create-external-tables",
    description="Create BigQuery external tables from Parquet files.",
    start_date=days_ago(1),
    catchup=False,
    schedule=[
        Dataset(application_main.parquet_filepath()),
        Dataset(interested_party.parquet_filepath()),
        Dataset(cipo_classification.parquet_filepath()),
        Dataset(opposition_case.parquet_filepath()),
    ],
):
    begin = EmptyOperator(task_id="begin-bq-create-external-tables")
    application_main_ext_table = create_external_table(application_main)
    interested_party_ext_table = create_external_table(interested_party)
    cipo_classification_ext_table = create_external_table(cipo_classification)
    opposition_case_ext_table = create_external_table(opposition_case)

    begin >> [
        application_main_ext_table,
        interested_party_ext_table,
        cipo_classification_ext_table,
        opposition_case_ext_table,
    ]
