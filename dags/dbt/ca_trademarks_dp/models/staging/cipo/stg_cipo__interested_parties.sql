{# 
Apply integer range partitioning on `party_type_code` to bucket data into 
12 partitions and cluster by `party_country_code` to improve performance of 
per-country analysis.
#}
with
interested_parties as (
    select * from {{ ref('base_cipo__interested_parties') }}
),
party_type_codes as (
    select * from {{ ref('party_type_codes') }}
),
join_interested_parties as (
    select
        application_number as application_id,
        party_type_code,
        party_type_description,
        party_name as party_name_original,
        {{ normalize_interested_party_names("party_name") }} as party_name,
        party_province_name as party_province,
        party_country_code as party_country,
        agent_number
    from interested_parties
    join party_type_codes
    using (party_type_code)
)

select * from join_interested_parties