select *
from {{ ref("stg_cipo__applications") }}
where
    wipo_status_description = "Registration published"
    and cipo_status_description = "Registered"
