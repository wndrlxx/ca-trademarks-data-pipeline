import os
from airflow.datasets import Dataset
from airflow.decorators import dag
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocDeleteClusterOperator,
    DataprocSubmitJobOperator,
)
from airflow.utils import trigger_rule
from airflow.utils.dates import days_ago
from include.ca_trademark_files import (
    TmApplicationMainFile,
    TmInterestedPartyFile,
    TmCipoClassificationFile,
    TmOppositionCaseFile,
)

REGION = os.environ.get("REGION", "us-west1")
DATA_BUCKET_NAME = os.environ.get("DATA_BUCKET", "ca-trademarks-2024-03-06")
AIRFLOW_BUCKET = os.environ.get("AIRFLOW_BUCKET", "ca-trademarks-composer2")
AIRFLOW_INCLUDE_PATH = f"gs://{AIRFLOW_BUCKET}/dags/include"

application_main = TmApplicationMainFile(DATA_BUCKET_NAME)
interested_party = TmInterestedPartyFile(DATA_BUCKET_NAME)
cipo_classification = TmCipoClassificationFile(DATA_BUCKET_NAME)
opposition_case = TmOppositionCaseFile(DATA_BUCKET_NAME)

# Spark configs
CLUSTER_NAME = "composer-spark-cluster"
CLUSTER_CONFIG = {
    "master_config": {
        "num_instances": 1,
        "machine_type_uri": "n1-standard-2",
        "disk_config": {"boot_disk_size_gb": 40},
    },
    "worker_config": {
        "num_instances": 2,
        "machine_type_uri": "n1-standard-2",
        "disk_config": {"boot_disk_size_gb": 40},
    },
    "endpoint_config": {"enable_http_port_access": True},
}
PYSPARK_JOB = {
    "placement": {"cluster_name": CLUSTER_NAME},
    "pyspark_job": {
        "main_python_file_uri": f"{AIRFLOW_INCLUDE_PATH}/spark_csv_to_parquet.py",
        "python_file_uris": [
            f"{AIRFLOW_INCLUDE_PATH}/ca_trademark_file_schemas.py"
        ],
    },
}


@dag(
    dag_id="spark-convert-csv-to-parquet",
    description="Trigger Dataproc Spark job that will create Parquet files.",
    start_date=days_ago(1),
    catchup=False,
    schedule=[
        Dataset(application_main.csv_filepath()),
        Dataset(interested_party.csv_filepath()),
        Dataset(cipo_classification.csv_filepath()),
        Dataset(opposition_case.csv_filepath()),
    ],
)
def convert_to_parquet():
    create_dataproc_cluster = DataprocCreateClusterOperator(
        task_id="create_dataproc_cluster",
        cluster_name=CLUSTER_NAME,
        cluster_config=CLUSTER_CONFIG,
        region=REGION,
    )

    submit_spark_to_parquet_job = DataprocSubmitJobOperator(
        task_id="submit_spark_to_parquet_job",
        region=REGION,
        job=PYSPARK_JOB,
        outlets=[
            Dataset(application_main.parquet_filepath()),
            Dataset(interested_party.parquet_filepath()),
            Dataset(cipo_classification.parquet_filepath()),
            Dataset(opposition_case.parquet_filepath()),
        ],
    )

    delete_dataproc_cluster = DataprocDeleteClusterOperator(
        task_id="delete_dataproc_cluster",
        cluster_name=CLUSTER_NAME,
        region=REGION,
        # Setting trigger_rule to ALL_DONE causes the cluster to be deleted
        # even if the Dataproc job fails.
        trigger_rule=trigger_rule.TriggerRule.ALL_DONE,
    )

    (
        create_dataproc_cluster
        >> submit_spark_to_parquet_job
        >> delete_dataproc_cluster
    )


convert_to_parquet()
