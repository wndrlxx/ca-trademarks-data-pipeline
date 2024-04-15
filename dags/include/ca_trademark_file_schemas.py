from pyspark.sql.types import (
    ByteType,
    DateType,
    IntegerType,
    LongType,
    StringType,
    StructField,
    StructType,
)


class TmFileBase:
    """Base class abstraction to encapsulate the schema definition and renamed columns."""

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.filename = None

    def csv_filename(self):
        return f"{self.filename}.csv"

    def parquet_filename(self):
        return f"{self.filename}.parquet"

    def csv_filepath(self):
        """Assumed to be in the raw/ directory"""
        return f"{self.bucket_fqn()}/raw/{self.csv_filename()}"

    def bucket_fqn(self):
        return f"gs://{self.bucket_name}"


class TmApplicationMainFile(TmFileBase):
    def __init__(self, bucket_name):
        super().__init__(bucket_name)
        self.filename = "TM_application_main_2024-03-06"

    schema = StructType(
        [
            StructField("application_number", IntegerType()),
            StructField("filing_date", DateType()),
            StructField("publication_date", DateType()),
            StructField("registration_date", DateType()),
            StructField("registration_office_country_code", StringType()),
            StructField("receiving_office_country_code", StringType()),
            StructField("receiving_office_date", DateType()),
            StructField("assigning_office_country_code", StringType()),
            StructField("registration_number", StringType()),
            StructField("legislation_description_code", ByteType()),
            StructField("filing_place", StringType()),
            StructField("application_reference_number", StringType()),
            StructField("application_language_code", StringType()),
            StructField("expiry_date", DateType()),
            StructField("termination_date", DateType()),
            StructField("wipo_status_code", ByteType()),
            StructField("current_status_date", DateType()),
            StructField("association_category_id", StringType()),
            StructField("ip_office_code", StringType()),
            StructField("associated_application_number", LongType()),
            StructField("mark_category", StringType()),
            StructField("divisional_application_country_code", StringType()),
            StructField("divisional_application_number", LongType()),
            StructField("divisional_application_date", DateType()),
            StructField("international_registration_number", IntegerType()),
            StructField("mark_type_code", ByteType()),
            StructField("mark_verbal_element_text", StringType()),
            StructField("mark_significant_verbal_element_text", StringType()),
            StructField("mark_translation_text", StringType()),
            StructField("expungement_indicator", ByteType()),
            StructField("distinctiveness_indicator", ByteType()),
            StructField("distinctiveness_description", StringType()),
            StructField("evidence_of_use_indicator", ByteType()),
            StructField("evidence_of_use_description", StringType()),
            StructField("restriction_of_use_description", StringType()),
            StructField("cipo_standard_message_description", StringType()),
            StructField("opposition_start_date", DateType()),
            StructField("opposition_end_date", DateType()),
            StructField("total_nice_classifications_number", IntegerType()),
            StructField("foreign_application_indicator", ByteType()),
            StructField("foreign_registration_indicator", ByteType()),
            StructField("used_in_canada_indicator", ByteType()),
            StructField("proposed_use_in_canada_indicator", ByteType()),
            StructField(
                "classification_term_office_country_code", StringType()
            ),
            StructField("classification_term_source_category", StringType()),
            StructField(
                "classification_term_english_description", StringType()
            ),
            StructField("publication_id", StringType()),
            StructField("publication_status", StringType()),
            StructField("authorization_of_use_date", DateType()),
            StructField("authorization_code", IntegerType()),
            StructField("authorization_description", StringType()),
            StructField("register_code", ByteType()),
            StructField("application_abandoned_date", DateType()),
            StructField("cipo_status_code", ByteType()),
            StructField("allowed_date", DateType()),
            StructField("renewal_date", DateType()),
            StructField("trademark_class_code", ByteType()),
            StructField(
                "geographical_indication_kind_category_code", ByteType()
            ),
            StructField(
                "geographical_indication_translation_sequence_number",
                IntegerType(),
            ),
            StructField(
                "geographical_indication_translation_text", StringType()
            ),
            StructField("doubtful_case_application_number", IntegerType()),
            StructField("doubtful_case_registration_number", StringType()),
        ]
    )
    renamed_columns = [
        "application_number",
        "filing_date",
        "publication_date",
        "registration_date",
        "registration_office_country_code",
        "receiving_office_country_code",
        "receiving_office_date",
        "assigning_office_country_code",
        "registration_number",
        "legislation_description_code",
        "filing_place",
        "application_reference_number",
        "application_language_code",
        "expiry_date",
        "termination_date",
        "wipo_status_code",
        "current_status_date",
        "association_category_id",
        "ip_office_code",
        "associated_application_number",
        "mark_category",
        "divisional_application_country_code",
        "divisional_application_number",
        "divisional_application_date",
        "international_registration_number",
        "mark_type_code",
        "mark_verbal_element_text",
        "mark_significant_verbal_element_text",
        "mark_translation_text",
        "expungement_indicator",
        "distinctiveness_indicator",
        "distinctiveness_description",
        "evidence_of_use_indicator",
        "evidence_of_use_description",
        "restriction_of_use_description",
        "cipo_standard_message_description",
        "opposition_start_date",
        "opposition_end_date",
        "total_nice_classifications_number",
        "foreign_application_indicator",
        "foreign_registration_indicator",
        "used_in_canada_indicator",
        "proposed_use_in_canada_indicator",
        "classification_term_office_country_code",
        "classification_term_source_category",
        "classification_term_english_description",
        "publication_id",
        "publication_status",
        "authorization_of_use_date",
        "authorization_code",
        "authorization_description",
        "register_code",
        "application_abandoned_date",
        "cipo_status_code",
        "allowed_date",
        "renewal_date",
        "trademark_class_code",
        "geographical_indication_kind_category_code",
        "geographical_indication_translation_sequence_number",
        "geographical_indication_translation_text",
        "doubtful_case_application_number",
        "doubtful_case_registration_number",
    ]


class TmInterestedPartyFile(TmFileBase):
    def __init__(self, bucket_name):
        super().__init__(bucket_name)
        self.filename = "TM_interested_party_2024-03-06"

    schema = StructType(
        [
            StructField("application_number", IntegerType()),
            StructField("party_type_code", ByteType()),
            StructField("party_language_code", StringType()),
            StructField("party_name", StringType()),
            StructField("party_address_line1", StringType()),
            StructField("party_address_line2", StringType()),
            StructField("party_address_line3", StringType()),
            StructField("party_address_line4", StringType()),
            StructField("party_address_line5", StringType()),
            StructField("party_province_name", StringType()),
            StructField("party_country_code", StringType()),
            StructField("party_postal_code", StringType()),
            StructField("contact_language_code", StringType()),
            StructField("contact_name", StringType()),
            StructField("contact_address_line1", StringType()),
            StructField("contact_address_line2", StringType()),
            StructField("contact_address_line3", StringType()),
            StructField("contact_province_name", StringType()),
            StructField("contact_country_code", StringType()),
            StructField("contact_postal_code", StringType()),
            StructField("current_owner_legal_name", StringType()),
            StructField("agent_number", IntegerType()),
        ]
    )
    renamed_columns = [
        "application_number",
        "party_type_code",
        "party_language_code",
        "party_name",
        "party_address_line1",
        "party_address_line2",
        "party_address_line3",
        "party_address_line4",
        "party_address_line5",
        "party_province_name",
        "party_country_code",
        "party_postal_code",
        "contact_language_code",
        "contact_name",
        "contact_address_line1",
        "contact_address_line2",
        "contact_address_line3",
        "contact_province_name",
        "contact_country_code",
        "contact_postal_code",
        "current_owner_legal_name",
        "agent_number",
    ]


class TmCipoClassificationFile(TmFileBase):
    def __init__(self, bucket_name):
        super().__init__(bucket_name)
        self.filename = "TM_cipo_classification_2024-03-06"

    schema = StructType(
        [
            StructField("application_number", IntegerType()),
            StructField("classification_kind_code", StringType()),
            StructField("nice_classification_code", ByteType()),
        ]
    )
    renamed_columns = [
        "application_number",
        "classification_kind_code",
        "nice_classification_code",
    ]


class TmOppositionCaseFile(TmFileBase):
    def __init__(self, bucket_name):
        super().__init__(bucket_name)
        self.filename = "TM_opposition_case_2024-03-06"

    schema = StructType(
        [
            StructField("application_number", IntegerType()),
            StructField("opposition_case_number", IntegerType()),
            StructField("opposition_case_type_english_name", StringType()),
            StructField("opposition_case_type_french_name", StringType()),
            StructField("opposition_date", DateType()),
            StructField("wipo_opposition_case_status", StringType()),
            StructField("opposition_wipo_status_date", DateType()),
            StructField("wipo_opposition_status_category", ByteType()),
            StructField("opposition_case_status_code", ByteType()),
            StructField("cipo_opposition_status_date", DateType()),
            StructField("contact_name_of_defendant", StringType()),
            StructField("contact_language_code_of_defendant", StringType()),
            StructField("contact_address_line_1_of_defendant", StringType()),
            StructField("contact_address_line_2_of_defendant", StringType()),
            StructField("contact_address_line_3_of_defendant", StringType()),
            StructField("contact_province_name_of_defendant", StringType()),
            StructField("contact_country_code_of_defendant", StringType()),
            StructField("contact_postal_code_of_defendant", StringType()),
            StructField("agent_name_of_defendant", StringType()),
            StructField("agent_language_code_of_defendant", StringType()),
            StructField("agent_address_line_1_of_defendant", StringType()),
            StructField("agent_address_line_2_of_defendant", StringType()),
            StructField("agent_address_line_3_of_defendant", StringType()),
            StructField("agent_province_name_of_defendant", StringType()),
            StructField("agent_country_code_of_defendant", StringType()),
            StructField("agent_postal_code_of_defendant", StringType()),
            StructField("plaintiff_name", StringType()),
            StructField("plaintiff_legal_name", StringType()),
            StructField("plaintiff_language_code", StringType()),
            StructField("plaintiff_address_line_1", StringType()),
            StructField("plaintiff_address_line_2", StringType()),
            StructField("plaintiff_address_line_3", StringType()),
            StructField("plaintiff_country_code", StringType()),
            StructField("contact_name_of_plaintiff", StringType()),
            StructField("contact_language_code_of_plaintiff", StringType()),
            StructField("contact_address_line_1_of_plaintiff", StringType()),
            StructField("contact_address_line_2_of_plaintiff", StringType()),
            StructField("contact_address_line_3_of_plaintiff", StringType()),
            StructField("contact_province_name_of_plaintiff", StringType()),
            StructField("contact_country_code_of_plaintiff", StringType()),
            StructField("contact_postal_code_of_plaintiff", StringType()),
            StructField("agent_number_of_plaintiff", IntegerType()),
            StructField("agent_name_of_plaintiff", StringType()),
            StructField("agent_language_code_of_plaintiff", StringType()),
            StructField("agent_address_line_1_of_plaintiff", StringType()),
            StructField("agent_address_line_2_of_plaintiff", StringType()),
            StructField("agent_address_line_3_of_plaintiff", StringType()),
            StructField("agent_province_name_of_plaintiff", StringType()),
            StructField("agent_country_code_of_plaintiff", StringType()),
            StructField("agent_postal_code_of_plaintiff", StringType()),
        ]
    )
    renamed_columns = [
        "application_number",
        "opposition_case_number",
        "opposition_case_type_english_name",
        "opposition_case_type_french_name",
        "opposition_date",
        "wipo_opposition_case_status",
        "opposition_wipo_status_date",
        "wipo_opposition_status_category",
        "opposition_case_status_code",
        "cipo_opposition_status_date",
        "contact_name_of_defendant",
        "contact_language_code_of_defendant",
        "contact_address_line_1_of_defendant",
        "contact_address_line_2_of_defendant",
        "contact_address_line_3_of_defendant",
        "contact_province_name_of_defendant",
        "contact_country_code_of_defendant",
        "contact_postal_code_of_defendant",
        "agent_name_of_defendant",
        "agent_language_code_of_defendant",
        "agent_address_line_1_of_defendant",
        "agent_address_line_2_of_defendant",
        "agent_address_line_3_of_defendant",
        "agent_province_name_of_defendant",
        "agent_country_code_of_defendant",
        "agent_postal_code_of_defendant",
        "plaintiff_name",
        "plaintiff_legal_name",
        "plaintiff_language_code",
        "plaintiff_address_line_1",
        "plaintiff_address_line_2",
        "plaintiff_address_line_3",
        "plaintiff_country_code",
        "contact_name_of_plaintiff",
        "contact_language_code_of_plaintiff",
        "contact_address_line_1_of_plaintiff",
        "contact_address_line_2_of_plaintiff",
        "contact_address_line_3_of_plaintiff",
        "contact_province_name_of_plaintiff",
        "contact_country_code_of_plaintiff",
        "contact_postal_code_of_plaintiff",
        "agent_number_of_plaintiff",
        "agent_name_of_plaintiff",
        "agent_language_code_of_plaintiff",
        "agent_address_line_1_of_plaintiff",
        "agent_address_line_2_of_plaintiff",
        "agent_address_line_3_of_plaintiff",
        "agent_province_name_of_plaintiff",
        "agent_country_code_of_plaintiff",
        "agent_postal_code_of_plaintiff",
    ]
