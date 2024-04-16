WITH

filings_with_year AS (
  SELECT
    application_id,
    EXTRACT(year FROM filing_date) AS year
  FROM
    {{ ref('stg_cipo__applications') }}
),

filings_with_decade AS (
  SELECT
    *,
    {{ year_to_decade(year) }} AS decade
  FROM
    filings_with_year 
),

filings_grouped_and_aggregated AS (
  SELECT
    decade,
    year,
    COUNT(*) AS count
  FROM
    filings_with_decade
  WHERE
    year IS NOT NULL
  GROUP BY
    decade,
    year
  ORDER BY
    year desc
)

select * from filings_grouped_and_aggregated