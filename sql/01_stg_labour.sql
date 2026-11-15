-- Stack the four MOM sources into one tidy table: year x industry x measure.
-- '-' (nil or negligible, per MOM notation) becomes NULL.
CREATE OR REPLACE TABLE stg_labour AS
SELECT year, industry, 'incidence' AS measure, TRY_CAST(NULLIF(incidence_of_retrenchment, '-') AS DOUBLE) AS value FROM raw_incidence
UNION ALL
SELECT year, industry, 'retrenched', TRY_CAST(NULLIF(retrench, '-') AS DOUBLE) FROM raw_retrenched
UNION ALL
SELECT year, industry, 'vacancy', TRY_CAST(NULLIF(job_vacancy, '-') AS DOUBLE) FROM raw_vacancy
UNION ALL
SELECT year, industry, 'resignation', TRY_CAST(NULLIF(resignation_rate, '-') AS DOUBLE) FROM raw_resignation;
