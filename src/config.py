"""Paths and dataset registry for the MOM labour-market project."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
SQL_DIR = ROOT / "sql"
OUTPUT_DIR = ROOT / "outputs"
DB_PATH = PROCESSED_DIR / "labour_market.duckdb"

FIRST_YEAR, LAST_YEAR = 2006, 2025  # SSIC 2005+ industry breakdown starts in 2006

# Ministry of Manpower datasets on data.gov.sg (Labour Market Survey, MRSD)
DATASETS = {
    "incidence": {
        "dataset_id": "d_8ee93a4e261908fafe878ea0bec29817",
        "title": "Incidence of Retrenchment by Industry - Annual",
        "file": "incidence_of_retrenchment_by_industry_annual.csv",
        "value_col": "incidence_of_retrenchment",
        "unit": "retrenched per 1,000 employees",
    },
    "retrenched": {
        "dataset_id": "d_661bf51b24d91dff23c053fc461c0923",
        "title": "Number of Retrenched Employees by Industry - Annual",
        "file": "retrenched_employees_by_industry_annual.csv",
        "value_col": "retrench",
        "unit": "persons (rounded to nearest 10)",
    },
    "vacancy": {
        "dataset_id": "d_01966fdb498fa7fa2863635e25539693",
        "title": "Number of Job Vacancy by Industry - Annual",
        "file": "job_vacancy_by_industry_annual.csv",
        "value_col": "job_vacancy",
        "unit": "vacancies (rounded to nearest 100)",
    },
    "resignation": {
        "dataset_id": "d_83f04fc0e00cb029000aa3bf8c5d0478",
        "title": "Average Monthly Resignation Rate by Industry - Annual",
        "file": "resignation_rate_by_industry_annual.csv",
        "value_col": "resignation_rate",
        "unit": "% of employees per month",
    },
}

# Level-1 industries kept for analysis. 'services' is the parent of SERVICE_SUBS.
SECTORS = ["manufacturing", "construction", "services", "others"]
SERVICE_SUBS = [
    "wholesale and retail trade",
    "transportation and storage",
    "accommodation and food services",
    "information and communications",
    "financial and insurance services",
    "real estate services",
    "professional services",
    "administrative and support services",
    "community, social and personal services",
]
INDUSTRIES = SECTORS[:3] + SERVICE_SUBS + ["others"]

# Rounding tolerance for hierarchy reconciliation (MOM rounds counts)
ROUNDING = {"retrenched": 10, "vacancy": 100}

BASELINE = (2015, 2019)  # pre-COVID baseline
LATEST = (2023, 2025)    # latest three years
