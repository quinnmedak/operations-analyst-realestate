{{ config(materialized='table') }}

SELECT
    s.ticker,
    s.date_day,
    s.open,
    s.high,
    s.low,
    s.close,
    s.volume,
    s.dividends
FROM {{ ref('stg_reit_daily_prices') }} s
INNER JOIN {{ ref('dim_reit') }} r ON s.ticker   = r.ticker
INNER JOIN {{ ref('dim_date') }} d ON s.date_day = d.date_day
