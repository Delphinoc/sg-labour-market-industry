-- Pre-COVID baseline (2015-19) vs latest three years (2023-25), per industry.
CREATE OR REPLACE TABLE mart_period_compare AS
WITH p AS (
    SELECT industry, parent, level, period,
        AVG(retrench_per_1000)    AS incidence,
        AVG(retrenched)           AS retrenched,
        AVG(vacancies)            AS vacancies,
        AVG(resignation_rate_pct) AS resignation,
        SUM(vacancies) / NULLIF(SUM(retrenched), 0) AS vac_per_retrenched
    FROM v_industry_year
    WHERE period IN ('baseline_2015_19', 'latest_2023_25')
    GROUP BY ALL
)
SELECT
    b.industry, b.parent, b.level,
    ROUND(b.incidence, 1)   AS incidence_base,   ROUND(l.incidence, 1)   AS incidence_latest,
    ROUND(l.incidence - b.incidence, 1) AS incidence_change,
    ROUND(b.retrenched)     AS retrenched_base,  ROUND(l.retrenched)     AS retrenched_latest,
    ROUND(b.vacancies)      AS vacancies_base,   ROUND(l.vacancies)      AS vacancies_latest,
    ROUND(b.vac_per_retrenched, 1) AS vpr_base,  ROUND(l.vac_per_retrenched, 1) AS vpr_latest,
    ROUND(b.resignation, 2) AS resignation_base, ROUND(l.resignation, 2) AS resignation_latest
FROM p b
JOIN p l ON l.industry = b.industry AND l.period = 'latest_2023_25'
WHERE b.period = 'baseline_2015_19';
