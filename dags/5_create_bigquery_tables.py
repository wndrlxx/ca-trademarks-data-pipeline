import os
from airflow import DAG
from airflow.datasets import Dataset
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryInsertJobOperator,
)
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago
from include.ca_trademark_files import (
    TmApplicationMainFile,
    TmInterestedPartyFile,
    TmCipoClassificationFile,
    TmOppositionCaseFile,
)

PROJECT_ID = os.environ.get("PROJECT", "ca-tm-dp")
DATASET_NAME = os.environ.get("BQ_DATASET", "ca_trademarks")
DATA_BUCKET_NAME = os.environ.get("DATA_BUCKET", "ca-trademarks-2024-03-06")
DATA_BUCKET_FQN = f"gs://{DATA_BUCKET_NAME}"
RAW_DATA_PATH = f"{DATA_BUCKET_FQN}/raw"
application_main = TmApplicationMainFile(DATA_BUCKET_NAME)
interested_party = TmInterestedPartyFile(DATA_BUCKET_NAME)
cipo_classification = TmCipoClassificationFile(DATA_BUCKET_NAME)
opposition_case = TmOppositionCaseFile(DATA_BUCKET_NAME)


def create_bq_insert_job_operator(table_name, create_query, outlets=[]):
    return BigQueryInsertJobOperator(
        task_id=f"create_{table_name}_table",
        configuration={
            "query": {
                "query": create_query,
                "useLegacySql": False,
            }
        },
        outlets=outlets,
    )


with DAG(
    dag_id="bigquery-create-tables",
    description="Partition and cluster tables",
    start_date=days_ago(1),
    catchup=False,
    schedule=[
        Dataset(application_main.bigquery_external_table_fqn()),
        Dataset(interested_party.bigquery_external_table_fqn()),
        Dataset(cipo_classification.bigquery_external_table_fqn()),
        Dataset(opposition_case.bigquery_external_table_fqn()),
    ],
):
    start = EmptyOperator(task_id="start")

    """ 
    Apply time-unit column partitioning on the year of the `registration_date` 
    to improve WHERE filtering performance for year range analysis. Cluster on 
    `wipo_status_code` column to improve JOIN and GROUP BY queries.
    """
    CREATE_APPLICATION_MAIN_TABLE_QUERY = (
        "CREATE OR REPLACE TABLE"
        f"  {PROJECT_ID}.{DATASET_NAME}.application_main "
        "PARTITION BY DATE_TRUNC(registration_date, YEAR) "
        "CLUSTER BY wipo_status_code "
        "AS ("
        f"  SELECT * FROM {PROJECT_ID}.{DATASET_NAME}.external_application_main"
        ");"
    )
    create_application_main_table = create_bq_insert_job_operator(
        table_name=application_main.table_id,
        create_query=CREATE_APPLICATION_MAIN_TABLE_QUERY,
        outlets=[Dataset(application_main.bigquery_fqn())],
    )

    """ 
    Apply integer range partitioning on `party_type_code` to bucket data into 
    12 partitions and cluster by `party_country_code` to improve performance of 
    per-country analysis.
    """
    CREATE_INTERESTED_PARTY_TABLE_QUERY = (
        "CREATE OR REPLACE TABLE "
        f"  {PROJECT_ID}.{DATASET_NAME}.interested_party "
        "PARTITION BY RANGE_BUCKET(party_type_code, GENERATE_ARRAY(1, 13, 1)) "
        "CLUSTER BY party_country_code "
        "AS ("
        f"  SELECT * FROM {PROJECT_ID}.{DATASET_NAME}.external_interested_party"
        ");"
    )
    create_interested_party_table = create_bq_insert_job_operator(
        table_name=interested_party.table_id,
        create_query=CREATE_INTERESTED_PARTY_TABLE_QUERY,
        outlets=[Dataset(interested_party.bigquery_fqn())],
    )

    """ 
    Apply integer range partitioning on `nice_classification_code` to group data
    into 45 partitions for improved filtering performance.
    """
    CREATE_CIPO_CLASSIFICATION_TABLE_QUERY = (
        "CREATE OR REPLACE TABLE "
        f"  {PROJECT_ID}.{DATASET_NAME}.cipo_classification "
        "PARTITION BY RANGE_BUCKET(nice_classification_code, GENERATE_ARRAY(1, 46, 1)) "
        "AS ("
        f"  SELECT * FROM {PROJECT_ID}.{DATASET_NAME}.external_cipo_classification"
        ");"
    )
    create_cipo_classification_table = create_bq_insert_job_operator(
        table_name=cipo_classification.table_id,
        create_query=CREATE_CIPO_CLASSIFICATION_TABLE_QUERY,
        outlets=[Dataset(cipo_classification.bigquery_fqn())],
    )

    """
    Apply clustering on `plaintiff_name` to improve performance of Top-N queries.
    """
    CREATE_OPPOSITION_CASE_TABLE_QUERY = (
        "CREATE OR REPLACE TABLE "
        f"  {PROJECT_ID}.{DATASET_NAME}.opposition_case "
        "CLUSTER BY plaintiff_name "
        "AS ("
        f"  SELECT * FROM {PROJECT_ID}.{DATASET_NAME}.external_opposition_case "
        ");"
    )
    create_opposition_case_table = create_bq_insert_job_operator(
        table_name=opposition_case.table_id,
        create_query=CREATE_OPPOSITION_CASE_TABLE_QUERY,
        outlets=[Dataset(opposition_case.bigquery_fqn())],
    )

    ADD_PK_CONSTRAINTS_QUERY = (
        f"ALTER TABLE {DATASET_NAME}.application_main "
        f"ADD PRIMARY KEY(application_number) NOT ENFORCED; "
        f"ALTER TABLE {DATASET_NAME}.interested_party "
        f"ADD PRIMARY KEY(application_number) NOT ENFORCED; "
        f"ALTER TABLE {DATASET_NAME}.cipo_classification "
        f"ADD PRIMARY KEY(application_number) NOT ENFORCED; "
        f"ALTER TABLE {DATASET_NAME}.opposition_case "
        f"ADD PRIMARY KEY(application_number) NOT ENFORCED;"
    )
    add_pk_constraints = BigQueryInsertJobOperator(
        task_id="add-pk-constraints",
        configuration={
            "query": {
                "query": ADD_PK_CONSTRAINTS_QUERY,
                "useLegacySql": False,
            }
        },
    )

    (
        start
        >> [
            create_application_main_table,
            create_interested_party_table,
            create_cipo_classification_table,
            create_opposition_case_table,
        ]
        >> add_pk_constraints
    )
