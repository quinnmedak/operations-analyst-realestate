{{ config(materialized='table') }}

SELECT
    ticker,
    company,
    property_type,
    primary_market
FROM {{ ref('reit_companies') }}
