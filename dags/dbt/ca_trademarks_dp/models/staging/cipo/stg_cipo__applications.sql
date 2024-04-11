{# """ 
Apply time-unit column partitioning on the year of the `registration_date` 
to improve WHERE filtering performance for year range analysis. Cluster on 
`wipo_status_code` column to improve JOIN and GROUP BY queries.
) #}
with
applications as (
    select * from {{ ref('base_cipo__applications') }}
),
wipo_status_codes as (
    select * from {{ ref('wipo_status_codes') }}
),
cipo_status_codes as (
    select * from {{ ref('cipo_status_codes') }}
),
join_applications as (
    select
        application_number as application_id,
        filing_date,
        publication_date,
        registration_date,
        wipo_status_code,
        wipo_status_description,
        cipo_status_code,
        cipo_status_description,
        mark_verbal_element_text as trademark_text,
        trademark_class_code
    from applications
    join wipo_status_codes
    using (wipo_status_code)
    join cipo_status_codes
    using (cipo_status_code)
)

select * from join_applications