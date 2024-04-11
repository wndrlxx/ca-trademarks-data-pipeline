with

source as (
  select * from {{ source('cipo', 'application_main') }}
),

applications as (
  select
    application_number,
    filing_date,
    publication_date,
    registration_date,
    wipo_status_code,
    cipo_status_code,
    mark_verbal_element_text,
    trademark_class_code
  from
    source
)

select * from applications