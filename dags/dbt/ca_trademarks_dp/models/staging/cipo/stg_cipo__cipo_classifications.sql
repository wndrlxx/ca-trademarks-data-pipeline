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