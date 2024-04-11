select plaintiff_name, count(*) as count
from {{ ref("stg_cipo__oppositions") }}
group by plaintiff_name
