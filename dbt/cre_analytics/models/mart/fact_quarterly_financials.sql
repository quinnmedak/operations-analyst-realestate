{{ config(materialized='table') }}

SELECT
    s.ticker,
    s.period_date,
    d.year,
    d.quarter,
    d.year_quarter,
    s.total_revenue,
    s.net_income,
    s.ebitda,
    s.operating_income,
    s.total_assets,
    s.total_debt,
    s.net_debt,
    s.long_term_debt
FROM {{ ref('stg_reit_quarterly_financials') }} s
INNER JOIN {{ ref('dim_reit') }} r ON s.ticker      = r.ticker
INNER JOIN {{ ref('dim_date') }} d ON s.period_date = d.date_day
