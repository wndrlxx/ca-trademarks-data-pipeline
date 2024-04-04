import os


class TmFileBase:
    """Base class abstraction to encapsulate the schema definition and renamed columns."""

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.project_id = os.environ.get("PROJECT_ID", "ca-tm-dp")
        self.dataset_id = os.environ.get("BQ_DATASET", "ca_trademarks")
        self.filename = ""
        self.table_id = ""
        self.source_url_path = "https://opic-cipo.ca/cipo/client_downloads/Trademarks_ResearcherDataset_CSVTXT_Q2FY2023"

    def source_url(self):
        return f"{self.source_url_path}/{self.zip_filename()}"

    def csv_filename(self):
        return f"{self.filename}.csv"

    def csv_zip_filename(self):
        return f"{self.filename}.csv.zip"

    def zip_filename(self):
        return f"{self.filename}.zip"

    def parquet_filename(self):
        return f"{self.filename}.parquet"

    def csv_filepath(self):
        """Assumed to be in the raw/ directory"""
        return f"{self.bucket_fqn()}/raw/{self.csv_filename()}"

    def csv_zip_filepath(self):
        """Assumed to be in the raw/compressed/ directory"""
        return f"{self.bucket_fqn()}/raw/compressed/{self.csv_zip_filename()}"

    def parquet_filepath(self):
        """Assumed to be in the transformed/ directory"""
        return f"{self.bucket_fqn()}/transformed/{self.parquet_filename()}"

    def bucket_fqn(self):
        return f"gs://{self.bucket_name}"

    def bigquery_fqn(self):
        return f"bigquery:{self.project_id}.{self.dataset_id}.{self.table_id}"


class TmApplicationMainFile(TmFileBase):
    def __init__(self, bucket_name):
        super().__init__(bucket_name)
        self.filename = "TM_application_main_2023-09-12"
        self.table_id = "application_main"


class TmInterestedPartyFile(TmFileBase):
    def __init__(self, bucket_name):
        super().__init__(bucket_name)
        self.filename = "TM_interested_party_2023-09-12"
        self.table_id = "interested_party"


class TmCipoClassificationFile(TmFileBase):
    def __init__(self, bucket_name):
        super().__init__(bucket_name)
        self.filename = "TM_cipo_classification_2023-09-12"
        self.table_id = "cipo_classification"


class TmOppositionCaseFile(TmFileBase):
    def __init__(self, bucket_name):
        super().__init__(bucket_name)
        self.filename = "TM_opposition_case_2023-09-12"
        self.table_id = "opposition_case"
