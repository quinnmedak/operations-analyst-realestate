{{ config(materialized='table') }}

WITH date_spine AS (
    SELECT
        DATEADD(day, SEQ4(), '2018-01-01'::DATE) AS date_day
    FROM TABLE(GENERATOR(rowcount => 4748))
)

SELECT
    date_day,
    YEAR(date_day)                                          AS year,
    QUARTER(date_day)                                       AS quarter,
    MONTH(date_day)                                         AS month,
    MONTHNAME(date_day)                                     AS month_name,
    DAY(date_day)                                           AS day_of_month,
    DAYOFWEEK(date_day)                                     AS day_of_week,
    DAYNAME(date_day)                                       AS day_name,
    CASE WHEN DAYOFWEEK(date_day) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend,
    YEAR(date_day) * 100 + QUARTER(date_day)                AS year_quarter,
    YEAR(date_day) * 100 + MONTH(date_day)                  AS year_month,
    YEAR(date_day)::VARCHAR || '-Q' || QUARTER(date_day)    AS quarter_label,
    TO_CHAR(date_day, 'Mon YYYY')                           AS month_label
FROM date_spine
