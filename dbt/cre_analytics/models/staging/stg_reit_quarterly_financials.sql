{{ config(materialized='view') }}

SELECT
    TICKER              AS ticker,
    PERIOD_DATE         AS period_date,
    TOTAL_REVENUE       AS total_revenue,
    NET_INCOME          AS net_income,
    EBITDA              AS ebitda,
    OPERATING_INCOME    AS operating_income,
    TOTAL_ASSETS        AS total_assets,
    TOTAL_DEBT          AS total_debt,
    NET_DEBT            AS net_debt,
    LONG_TERM_DEBT      AS long_term_debt
FROM {{ source('raw', 'reit_quarterly_financials') }}
