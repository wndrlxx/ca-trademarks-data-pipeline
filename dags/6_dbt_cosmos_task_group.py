import os
from pathlib import Path
from airflow.datasets import Dataset
from airflow.decorators import dag
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.constants import ExecutionMode
from include.ca_trademark_files import (
    TmApplicationMainFile,
    TmInterestedPartyFile,
    TmCipoClassificationFile,
    TmOppositionCaseFile,
)

DEFAULT_DBT_ROOT_PATH = Path(__file__).parent / "dbt"
DBT_ROOT_PATH = Path(os.getenv("DBT_ROOT_PATH", DEFAULT_DBT_ROOT_PATH))
PROFILES_FILE_PATH = Path(DBT_ROOT_PATH, "ca_trademarks_dp", "profiles.yml")
DATA_BUCKET_NAME = os.environ.get("DATA_BUCKET", "ca-trademarks-2024-03-06")
PROJECT_ID = os.environ.get("PROJECT", "ca-tm-dp")
DATASET_ID = os.environ.get("BQ_DATASET", "ca_trademarks")
application_main = TmApplicationMainFile(DATA_BUCKET_NAME)
interested_party = TmInterestedPartyFile(DATA_BUCKET_NAME)
cipo_classification = TmCipoClassificationFile(DATA_BUCKET_NAME)
opposition_case = TmOppositionCaseFile(DATA_BUCKET_NAME)

profile_config = ProfileConfig(
    profile_name="ca_trademarks_dp",
    target_name="prod",
    profiles_yml_filepath=PROFILES_FILE_PATH,
)


@dag(
    dag_id="dbt",
    description="Run dbt project as a task group",
    start_date=days_ago(1),
    catchup=False,
    schedule=[
        Dataset(application_main.bigquery_fqn()),
        Dataset(interested_party.bigquery_fqn()),
        Dataset(opposition_case.bigquery_fqn()),
        Dataset(cipo_classification.bigquery_fqn()),
    ],
)
def simple_task_group():
    dbt_project = DbtTaskGroup(
        group_id="ca_trademarks_dbt_project",
        project_config=ProjectConfig(
            DBT_ROOT_PATH / "ca_trademarks_dp",
        ),
        profile_config=profile_config,
        execution_config=ExecutionConfig(
            execution_mode=ExecutionMode.VIRTUALENV,
        ),
    )

    post_dbt = EmptyOperator(
        task_id="post_dbt",
        outlets=[
            Dataset(f"bigquery:{PROJECT_ID}.{DATASET_ID}.plaintiffs"),
            Dataset(f"bigquery:{PROJECT_ID}.{DATASET_ID}.filings"),
            Dataset(f"bigquery:{PROJECT_ID}.{DATASET_ID}.registrations"),
            Dataset(f"bigquery:{PROJECT_ID}.{DATASET_ID}.trademark_owners"),
        ],
    )

    dbt_project >> post_dbt


simple_task_group()
