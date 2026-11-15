"""Refresh data/raw/ from the data.gov.sg API (MOM datasets).

Keeps 2006 onwards and the Level-1 industries used in the analysis, in the
API's own long format (year, industry, value). '-' (nil/negligible) is kept
as published; the pipeline treats it as missing.

    python scripts/download_data.py
    python -m src.pipeline
    pytest
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import DATASETS, FIRST_YEAR, INDUSTRIES, RAW_DIR  # noqa: E402

API = "https://data.gov.sg/api/action/datastore_search"


def fetch(dataset_id: str) -> pd.DataFrame:
    records, offset = [], 0
    while True:
        resp = requests.get(API, params={"resource_id": dataset_id, "limit": 5000, "offset": offset}, timeout=30)
        resp.raise_for_status()
        result = resp.json()["result"]
        records += result["records"]
        offset += len(result["records"])
        if offset >= result["total"] or not result["records"]:
            break
        time.sleep(1)
    return pd.DataFrame(records).drop(columns=["_id"], errors="ignore")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name, meta in DATASETS.items():
        df = fetch(meta["dataset_id"])
        df["year"] = df["year"].astype(int)
        df = df[(df["year"] >= FIRST_YEAR) & df["industry"].isin(INDUSTRIES)]
        df = df[["year", "industry", meta["value_col"]]]
        df.to_csv(RAW_DIR / meta["file"], index=False)
        print(f"{name}: {len(df)} rows -> {meta['file']}")
        time.sleep(1)


if __name__ == "__main__":
    main()
