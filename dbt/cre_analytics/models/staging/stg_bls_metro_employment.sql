{{ config(materialized='view') }}

SELECT
    SERIES_ID                                                                           AS series_id,
    METRO                                                                               AS metro,
    SUPERSECTOR                                                                         AS supersector,
    YEAR                                                                                AS year,
    REPLACE(PERIOD, 'M', '')::INTEGER                                                   AS month,
    PERIOD_NAME                                                                         AS period_name,
    EMPLOYMENT_THOUSANDS                                                                AS employment_thousands,
    TO_DATE(YEAR::VARCHAR || '-' || LPAD(REPLACE(PERIOD, 'M', ''), 2, '0') || '-01')   AS date_day
FROM {{ source('raw', 'bls_metro_employment') }}
WHERE PERIOD != 'M13'
