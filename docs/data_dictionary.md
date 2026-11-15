# Data dictionary

## Sources (Ministry of Manpower, Labour Market Survey, via data.gov.sg)

| Key | data.gov.sg dataset | Measure | Unit |
|---|---|---|---|
| incidence | `d_8ee93a4e261908fafe878ea0bec29817` | Incidence of retrenchment | retrenched per 1,000 employees |
| retrenched | `d_661bf51b24d91dff23c053fc461c0923` | Number of retrenched employees | persons, rounded to nearest 10 |
| vacancy | `d_01966fdb498fa7fa2863635e25539693` | Number of job vacancies (June) | vacancies, rounded to nearest 100 |
| resignation | `d_83f04fc0e00cb029000aa3bf8c5d0478` | Average monthly resignation rate | % of employees |

Scope kept: 2006–2025 (SSIC 2005+ breakdown) and 13 industries (12 Level-1/2 plus "others").
MOM notation `-` means nil or negligible; the pipeline stores it as NULL.
Before 2006 the survey covered private establishments with at least 25 employees only; from 2006 it includes the public sector.

## Tables

| Table | Grain | Fields |
|---|---|---|
| `stg_labour` | year × industry × measure | `year`, `industry`, `measure`, `value` |
| `dim_industry` | industry | `industry_key`, `industry`, `parent` (`total`/`services`), `level`, `sort_order` |
| `dim_year` | year | `year_key`, `year`, `period` (`baseline_2015_19`, `covid_2020_21`, `latest_2023_25`, `other`), `is_covid_shock` |
| `fct_industry_year` | industry × year | `industry_key`, `year_key`, `retrench_per_1000`, `retrenched`, `vacancies`, `resignation_rate_pct` |
| `v_industry_year` | industry × year | labelled fact + `vacancies_per_retrenched` |
| `mart_period_compare` | industry | 2015–19 vs 2023–25 averages for each measure; `vpr_*` = summed vacancies ÷ summed retrenchments |
| `mart_industry_segments` | industry (11, excl. services aggregate and others) | `incidence_latest`, `vpr_latest`, `segment` |
| `mart_economy_trend` | year | whole-economy retrenched, vacancies, vacancies per retrenched worker |

## Segment rule (`mart_industry_segments`)

Using 2023–25 averages and the median across the 11 industries (ties count as high):

| Retrenchment incidence | Vacancies per retrenched worker | Segment |
|---|---|---|
| ≥ median | < median | Restructuring |
| ≥ median | ≥ median | Churn |
| < median | ≥ median | Tight |
| < median | < median | Stable |

Transport & storage sits exactly at both medians, so its "Churn" label is borderline.
