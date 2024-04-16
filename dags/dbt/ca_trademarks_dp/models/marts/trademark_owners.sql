select party_name, count(*) as count
from {{ ref("int_applications_filtered_by_active") }}
join {{ ref("stg_cipo__interested_parties") }} using (application_id)
where party_type_description = "Registrant"
group by party_name
