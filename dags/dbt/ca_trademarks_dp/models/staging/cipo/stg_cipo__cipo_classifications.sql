{# """ 
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
  ) #}
with 
cipo_classifications as (
    select * from {{ ref('base_cipo__cipo_classifications') }}
),
nice_classification_codes as (
    select * from {{ ref('nice_classification_codes') }}
),
join_cipo_classifications as (
    select
        application_number as application_id,
        nice_classification_code,
        nice_classification_description
    from nice_classification_codes
    join cipo_classifications
    using (nice_classification_code)
)

select * from join_cipo_classifications