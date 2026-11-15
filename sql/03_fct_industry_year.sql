-- Fuse the four sources at industry x year grain (one row each).
CREATE OR REPLACE TABLE fct_industry_year AS
SELECT
    d.industry_key,
    s.year AS year_key,
    MAX(CASE WHEN measure = 'incidence'   THEN value END) AS retrench_per_1000,
    MAX(CASE WHEN measure = 'retrenched'  THEN value END) AS retrenched,
    MAX(CASE WHEN measure = 'vacancy'     THEN value END) AS vacancies,
    MAX(CASE WHEN measure = 'resignation' THEN value END) AS resignation_rate_pct
FROM stg_labour s
JOIN dim_industry d USING (industry)
GROUP BY d.industry_key, s.year;

-- Analyst view with labels and derived metrics
CREATE OR REPLACE VIEW v_industry_year AS
SELECT
    d.industry, d.parent, d.level, y.year, y.period,
    f.retrench_per_1000, f.retrenched, f.vacancies, f.resignation_rate_pct,
    -- Vacancies per retrenched worker: >1 means more open jobs than job losses
    CASE WHEN f.retrenched > 0 THEN f.vacancies / f.retrenched END AS vacancies_per_retrenched
FROM fct_industry_year f
JOIN dim_industry d USING (industry_key)
JOIN dim_year y USING (year_key);
