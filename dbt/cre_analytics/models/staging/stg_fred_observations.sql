{{ config(materialized='view') }}

SELECT
    SERIES_ID               AS series_id,
    TRY_TO_DATE(DATE)       AS obs_date,
    TRY_TO_DOUBLE(VALUE)    AS value
FROM {{ source('raw', 'fred_observations') }}
WHERE TRY_TO_DATE(DATE) IS NOT NULL
  AND TRY_TO_DOUBLE(VALUE) IS NOT NULL
