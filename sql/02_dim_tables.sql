CREATE OR REPLACE TABLE dim_industry AS
SELECT
    ROW_NUMBER() OVER (ORDER BY sort_order) AS industry_key,
    industry,
    parent,
    level,
    sort_order
FROM (VALUES
    ('manufacturing', 'total', 1, 1),
    ('construction', 'total', 1, 2),
    ('services', 'total', 1, 3),
    ('wholesale and retail trade', 'services', 2, 4),
    ('transportation and storage', 'services', 2, 5),
    ('accommodation and food services', 'services', 2, 6),
    ('information and communications', 'services', 2, 7),
    ('financial and insurance services', 'services', 2, 8),
    ('real estate services', 'services', 2, 9),
    ('professional services', 'services', 2, 10),
    ('administrative and support services', 'services', 2, 11),
    ('community, social and personal services', 'services', 2, 12),
    ('others', 'total', 1, 13)
) AS t(industry, parent, level, sort_order);

CREATE OR REPLACE TABLE dim_year AS
SELECT
    year AS year_key,
    year,
    CASE WHEN year BETWEEN 2015 AND 2019 THEN 'baseline_2015_19'
         WHEN year BETWEEN 2023 AND 2025 THEN 'latest_2023_25'
         WHEN year IN (2020, 2021) THEN 'covid_2020_21'
         ELSE 'other' END AS period,
    year = 2020 AS is_covid_shock
FROM (SELECT DISTINCT year FROM stg_labour);
