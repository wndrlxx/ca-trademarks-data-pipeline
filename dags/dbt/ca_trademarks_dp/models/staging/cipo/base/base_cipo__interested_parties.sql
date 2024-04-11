with

source as (
  select * from {{ source('cipo', 'interested_party') }}
),

interested_parties as (
  select
    application_number,
    party_type_code,
    party_name,
    party_province_name,
    party_country_code,
    agent_number
  from
    source
)

select * from interested_parties