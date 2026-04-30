{{ config(materialized='view') }}

SELECT
    TICKER      AS ticker,
    DATE        AS date_day,
    OPEN        AS open,
    HIGH        AS high,
    LOW         AS low,
    CLOSE       AS close,
    VOLUME      AS volume,
    DIVIDENDS   AS dividends
FROM {{ source('raw', 'reit_daily_prices') }}
