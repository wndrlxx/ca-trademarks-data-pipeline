WITH

registrations_with_year AS (
  SELECT
    application_id,
    EXTRACT(year FROM registration_date) AS year
  FROM
    {{ ref('stg_cipo__applications') }}
),

registrations_with_decade AS (
  SELECT
    *,
    {{ year_to_decade(year) }} AS decade
  FROM
    registrations_with_year 
),

registrations_grouped_and_aggregated AS (
  SELECT
    decade,
    year,
    COUNT(*) AS count
  FROM
    registrations_with_decade
  WHERE
    year IS NOT NULL
  GROUP BY
    decade,
    year
  ORDER BY
    year desc
)

select * from registrations_grouped_and_aggregated