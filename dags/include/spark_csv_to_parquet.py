from ca_trademark_file_schemas import (
    TmApplicationMainFile,
    TmInterestedPartyFile,
    TmCipoClassificationFile,
    TmOppositionCaseFile,
)
from pyspark.sql import SparkSession

# TODO: remove hardcoded values. How to set ENV vars on Spark?
# see https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/dataproc_cluster#initialization_action
# see https://stackoverflow.com/questions/61207679/setting-environment-variables-on-dataproc-cluster-nodes
DATA_BUCKET_NAME = "ca-trademarks-2023-09-12"
DATA_BUCKET_FQN = f"gs://{DATA_BUCKET_NAME}"
RAW_DATA_PATH = f"{DATA_BUCKET_FQN}/raw"
TRANSFORMED_DATA_PATH = f"{DATA_BUCKET_FQN}/transformed"

spark = (
    SparkSession.builder.appName("Canadian Trademark Applications")
    .config("spark.sql.legacy.parquet.datetimeRebaseModeInWrite", "CORRECTED")
    .getOrCreate()
)


def convert_to_parquet(TmCSV):
    df = (
        spark.read.options(delimiter="|", header=True, enforceSchema=True)
        .schema(TmCSV.schema)
        .csv(TmCSV.csv_filepath(RAW_DATA_PATH))
    )
    df = df.toDF(*TmCSV.renamed_columns)
    output_dir = f"{TRANSFORMED_DATA_PATH}/{TmCSV.filename}"
    df.write.parquet(output_dir, mode="overwrite")


convert_to_parquet(TmApplicationMainFile(DATA_BUCKET_FQN))
convert_to_parquet(TmInterestedPartyFile(DATA_BUCKET_FQN))
convert_to_parquet(TmCipoClassificationFile(DATA_BUCKET_FQN))
convert_to_parquet(TmOppositionCaseFile(DATA_BUCKET_FQN))
