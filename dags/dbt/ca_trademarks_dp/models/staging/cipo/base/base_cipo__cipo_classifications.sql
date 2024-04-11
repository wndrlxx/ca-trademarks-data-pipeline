with 

source as (
  select * from {{ source('cipo', 'cipo_classification') }}
), 

cipo_classifications as (
  select 
    application_number,
    nice_classification_code
  from
    source
)

select * from cipo_classifications