-- Classify services and goods industries on two axes, latest period (2023-25):
--   retrenchment incidence vs the median across industries
--   vacancies per retrenched worker vs the median across industries
CREATE OR REPLACE TABLE mart_industry_segments AS
WITH x AS (
    SELECT * FROM mart_period_compare
    WHERE industry NOT IN ('services', 'others')   -- parent aggregate and residual excluded
), med AS (
    SELECT MEDIAN(incidence_latest) AS m_inc, MEDIAN(vpr_latest) AS m_vpr FROM x
)
SELECT
    x.industry, x.incidence_latest, x.vpr_latest, x.incidence_change,
    CASE
        WHEN x.incidence_latest >= m_inc AND x.vpr_latest <  m_vpr THEN 'Restructuring: high job losses, few openings'
        WHEN x.incidence_latest >= m_inc AND x.vpr_latest >= m_vpr THEN 'Churn: high job losses and many openings'
        WHEN x.incidence_latest <  m_inc AND x.vpr_latest >= m_vpr THEN 'Tight: low job losses, many openings'
        ELSE 'Stable: low job losses, fewer openings'
    END AS segment
FROM x, med
ORDER BY x.incidence_latest DESC;
