WITH

filings_with_year AS (
  SELECT
    EXTRACT(year FROM filing_date) AS year,
    nice_classification_description
  FROM
    {{ ref('stg_cipo__applications') }}
  JOIN
    {{ ref('stg_cipo__cipo_classifications') }}
  USING (application_id)
),

filings_with_decade AS (
  SELECT
    {{ year_to_decade(year) }} AS decade,
    *
  FROM
    filings_with_year 
),

filings_grouped_and_aggregated AS (
  SELECT
    decade,
    year,
    nice_classification_description,
    COUNT(*) AS count
  FROM
    filings_with_decade
  WHERE
    year IS NOT NULL
  GROUP BY
    decade,
    year,
    nice_classification_description
  ORDER BY
    year desc
)

select * from filings_grouped_and_aggregated