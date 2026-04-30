{{ config(materialized='table') }}

WITH quarterly AS (
    SELECT
        YEAR(obs_date)    AS year,
        QUARTER(obs_date) AS quarter,
        series_id,
        AVG(value)        AS avg_value
    FROM {{ ref('stg_fred_observations') }}
    GROUP BY 1, 2, 3
)

SELECT
    year,
    quarter,
    year * 100 + quarter                                                    AS year_quarter,
    MAX(CASE WHEN series_id = 'FEDFUNDS'       THEN avg_value END)          AS fedfunds,
    MAX(CASE WHEN series_id = 'DGS10'          THEN avg_value END)          AS dgs10,
    MAX(CASE WHEN series_id = 'MORTGAGE30US'   THEN avg_value END)          AS mortgage30us,
    MAX(CASE WHEN series_id = 'T10Y2Y'         THEN avg_value END)          AS t10y2y,
    MAX(CASE WHEN series_id = 'UNRATE'         THEN avg_value END)          AS unrate,
    MAX(CASE WHEN series_id = 'PAYEMS'         THEN avg_value END)          AS payems,
    MAX(CASE WHEN series_id = 'ECOMPCTNSA'     THEN avg_value END)          AS ecompctnsa,
    MAX(CASE WHEN series_id = 'DRCRELEXFACBS'  THEN avg_value END)          AS drcrelexfacbs,
    MAX(CASE WHEN series_id = 'CREACBW027SBOG' THEN avg_value END)          AS creacbw027sbog
FROM quarterly
GROUP BY year, quarter
ORDER BY year, quarter
