with
source as (select * from {{ source("cipo", "opposition_case") }}),
renamed as (
    select
        application_number as application_id,
        opposition_date,

        -- defendant
        contact_name_of_defendant as defendant_name,
        contact_country_code_of_defendant as defendant_country,

        -- defendant agent
        agent_name_of_defendant as defendant_agent_name,
        agent_country_code_of_defendant as defendant_agent_country,

        -- plaintiff
        contact_name_of_plaintiff as plaintiff_name_original,
        {{ normalize_interested_party_names("contact_name_of_plaintiff") }}
        as plaintiff_name,
        contact_country_code_of_plaintiff as plaintiff_country,

        -- plaintiff agent
        agent_name_of_plaintiff as plaintiff_agent_name,
        agent_country_code_of_plaintiff as plaintiff_agent_country
    from source
)

select * from renamed
