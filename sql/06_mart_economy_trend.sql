-- Whole-economy totals (manufacturing + construction + services + others)
CREATE OR REPLACE TABLE mart_economy_trend AS
SELECT
    year,
    SUM(retrenched) AS retrenched,
    SUM(vacancies)  AS vacancies,
    ROUND(SUM(vacancies) / SUM(retrenched), 1) AS vacancies_per_retrenched
FROM v_industry_year
WHERE level = 1
GROUP BY year
ORDER BY year;
