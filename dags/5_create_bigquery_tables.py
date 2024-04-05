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

PROJECT_ID = os.environ.get("PROJECT_ID", "ca-tm-dp")
DATASET_NAME = os.environ.get("BQ_DATASET", "ca_trademarks")
DATA_BUCKET_NAME = os.environ.get("DATA_BUCKET", "ca-trademarks-2023-09-12")
DATA_BUCKET_FQN = f"gs://{DATA_BUCKET_NAME}"
RAW_DATA_PATH = f"{DATA_BUCKET_FQN}/raw"
application_main = TmApplicationMainFile(DATA_BUCKET_NAME)
interested_party = TmInterestedPartyFile(DATA_BUCKET_NAME)
cipo_classification = TmCipoClassificationFile(DATA_BUCKET_NAME)
opposition_case = TmOppositionCaseFile(DATA_BUCKET_NAME)


def create_bq_insert_job_operator(table_name, create_query):
    return BigQueryInsertJobOperator(
        task_id=f"create_{table_name}_table",
        configuration={
            "query": {
                "query": create_query,
                "useLegacySql": False,
            }
        },
    )


def create_bq_table_from_csv(table_name: str, csv_header_col: str):
    create_query = (
        f"LOAD DATA OVERWRITE {DATASET_NAME}.{table_name}"
        f"{csv_header_col} "
        f"FROM FILES ( "
        f"  format = 'CSV', "
        f"  field_delimiter = ';', "
        f"  skip_leading_rows = 1, "
        f"  uris = ['{RAW_DATA_PATH}/{table_name}.csv']);"
    )
    return create_bq_insert_job_operator(table_name, create_query)


with DAG(
    dag_id="bigquery-create-tables",
    description="Create status code tables and partitioned/clustered application_main table",
    start_date=days_ago(1),
    catchup=False,
    schedule=[
        Dataset(application_main.bigquery_fqn()),
        Dataset(interested_party.bigquery_fqn()),
        Dataset(cipo_classification.bigquery_fqn()),
        Dataset(opposition_case.bigquery_fqn()),
    ],
):
    start = EmptyOperator(task_id="start")
    create_cipo_status_code_table = create_bq_table_from_csv(
        table_name="cipo_status_code",
        csv_header_col="(cipo_status_code INT64, description STRING) ",
    )
    create_wipo_status_code_table = create_bq_table_from_csv(
        table_name="wipo_status_code",
        csv_header_col="(wipo_status_code INT64, description STRING) ",
    )
    create_nice_classification_code_table = create_bq_table_from_csv(
        table_name="nice_classification_code",
        csv_header_col="(nice_classification_code INT64, description STRING) ",
    )
    create_party_type_code_table = create_bq_table_from_csv(
        table_name="party_type_code",
        csv_header_col="(party_type_code INT64, description STRING) ",
    )

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
        table_name="application_main",
        create_query=CREATE_APPLICATION_MAIN_TABLE_QUERY,
    )

    """ `party_type_code` values range from 1 to 12 """
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
        table_name="interested_party",
        create_query=CREATE_INTERESTED_PARTY_TABLE_QUERY,
    )

    """ `nice_classification_code` values range from 1 to 45 """
    CREATE_CIPO_CLASSIFICATION_TABLE_QUERY = (
        "CREATE OR REPLACE TABLE "
        f"  {PROJECT_ID}.{DATASET_NAME}.cipo_classification "
        "PARTITION BY RANGE_BUCKET(nice_classification_code, GENERATE_ARRAY(1, 46, 1)) "
        "AS ("
        f"  SELECT * FROM {PROJECT_ID}.{DATASET_NAME}.external_cipo_classification"
        ");"
    )
    create_cipo_classification_table = create_bq_insert_job_operator(
        table_name="cipo_classification",
        create_query=CREATE_CIPO_CLASSIFICATION_TABLE_QUERY,
    )

    CREATE_OPPOSITION_CASE_TABLE_QUERY = (
        "CREATE OR REPLACE TABLE "
        f"  {PROJECT_ID}.{DATASET_NAME}.opposition_case "
        "CLUSTER BY plaintiff_name "
        "AS ("
        f"  SELECT * FROM {PROJECT_ID}.{DATASET_NAME}.external_opposition_case "
        ");"
    )
    create_opposition_case_table = create_bq_insert_job_operator(
        table_name="opposition_case",
        create_query=CREATE_OPPOSITION_CASE_TABLE_QUERY,
    )

    ADD_PK_CONSTRAINTS_QUERY = (
        f"ALTER TABLE {DATASET_NAME}.cipo_status_code "
        f"ADD PRIMARY KEY(cipo_status_code) NOT ENFORCED; "
        f"ALTER TABLE {DATASET_NAME}.wipo_status_code "
        f"ADD PRIMARY KEY(wipo_status_code) NOT ENFORCED; "
        f"ALTER TABLE {DATASET_NAME}.nice_classification_code "
        f"ADD PRIMARY KEY(nice_classification_code) NOT ENFORCED; "
        f"ALTER TABLE {DATASET_NAME}.party_type_code "
        f"ADD PRIMARY KEY(party_type_code) NOT ENFORCED; "
        f"ALTER TABLE {DATASET_NAME}.application_main "
        f"ADD PRIMARY KEY(application_number) NOT ENFORCED, "
        f"ADD FOREIGN KEY(wipo_status_code) REFERENCES "
        f"{DATASET_NAME}.wipo_status_code(wipo_status_code) NOT ENFORCED, "
        f"ADD FOREIGN KEY(cipo_status_code) REFERENCES "
        f"{DATASET_NAME}.cipo_status_code(cipo_status_code) NOT ENFORCED; "
        f"ALTER TABLE {DATASET_NAME}.interested_party "
        f"ADD PRIMARY KEY(application_number) NOT ENFORCED, "
        f"ADD FOREIGN KEY(party_type_code) REFERENCES "
        f"{DATASET_NAME}.party_type_code(party_type_code) NOT ENFORCED;"
        f"ALTER TABLE {DATASET_NAME}.cipo_classification "
        f"ADD PRIMARY KEY(application_number) NOT ENFORCED, "
        f"ADD FOREIGN KEY(nice_classification_code) REFERENCES "
        f"{DATASET_NAME}.nice_classification_code(nice_classification_code) NOT ENFORCED;"
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
            create_wipo_status_code_table,
            create_cipo_status_code_table,
            create_nice_classification_code_table,
            create_party_type_code_table,
            create_application_main_table,
            create_interested_party_table,
            create_cipo_classification_table,
            create_opposition_case_table,
        ]
        >> add_pk_constraints
    )
