{{ config(materialized='table') }}

SELECT
    s.series_id,
    s.metro,
    s.supersector,
    s.year,
    s.month,
    s.period_name,
    s.date_day,
    s.employment_thousands
FROM {{ ref('stg_bls_metro_employment') }} s
INNER JOIN {{ ref('dim_date') }} d ON s.date_day = d.date_day
