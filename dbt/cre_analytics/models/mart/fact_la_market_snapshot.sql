WITH stg AS (
    SELECT * FROM {{ ref('stg_la_marketbeat') }}
)

SELECT
    property_type,
    submarket,
    period,
    period_date,
    source,
    vacancy_rate,
    vacancy_rate_bps_qoq,
    vacancy_rate_bps_yoy,
    qtr_net_absorption_sf,
    ytd_net_absorption_sf,
    absorption_context,
    asking_rent_psf,
    asking_rent_type
FROM stg
