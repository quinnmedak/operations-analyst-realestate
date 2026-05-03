{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM {{ ref('la_marketbeat') }}
)

SELECT
    property_type,
    submarket,
    period,
    CAST(period_date AS DATE)          AS period_date,
    source,
    CAST(vacancy_rate AS FLOAT)        AS vacancy_rate,
    CAST(vacancy_rate_bps_qoq AS INT)  AS vacancy_rate_bps_qoq,
    CAST(vacancy_rate_bps_yoy AS INT)  AS vacancy_rate_bps_yoy,
    CAST(qtr_net_absorption_sf AS INT) AS qtr_net_absorption_sf,
    CAST(ytd_net_absorption_sf AS INT) AS ytd_net_absorption_sf,
    absorption_context,
    CAST(asking_rent_psf AS FLOAT)     AS asking_rent_psf,
    asking_rent_type
FROM source
