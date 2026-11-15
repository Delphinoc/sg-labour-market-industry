"""Load raw MOM files, run checks, build DuckDB models, export marts and charts."""
from __future__ import annotations

import json
import sys

import duckdb
import pandas as pd

from src.checks import run_checks
from src.config import DATASETS, DB_PATH, PROCESSED_DIR, RAW_DIR, SQL_DIR


def load_raw() -> dict[str, pd.DataFrame]:
    return {k: pd.read_csv(RAW_DIR / m["file"], dtype={m["value_col"]: str}) for k, m in DATASETS.items()}


def build(con: duckdb.DuckDBPyConnection, raw: dict[str, pd.DataFrame]) -> None:
    for name, df in raw.items():
        con.register(f"_{name}", df)
        con.execute(f"CREATE OR REPLACE TABLE raw_{name} AS SELECT * FROM _{name}")
    for f in sorted(SQL_DIR.glob("*.sql")):
        con.execute(f.read_text())


def main() -> int:
    raw = load_raw()
    results = run_checks(raw)
    for r in results:
        flag = "PASS" if r.passed else ("FAIL" if r.severity == "error" else "WARN")
        print(f"[{flag}] {r.rule} {('- ' + r.detail) if r.detail and not r.passed else ''}")
    if any(not r.passed and r.severity == "error" for r in results):
        print("Errors found; stopping.")
        return 1
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = duckdb.connect(str(DB_PATH))
    build(con, raw)
    for t in ["v_industry_year", "mart_period_compare", "mart_industry_segments", "mart_economy_trend"]:
        con.execute(f"SELECT * FROM {t}").df().to_csv(PROCESSED_DIR / f"{t}.csv", index=False)
    (PROCESSED_DIR / "dq_results.json").write_text(json.dumps([r.__dict__ | {"passed": bool(r.passed)} for r in results], indent=2))
    con.close()
    print("Built", DB_PATH.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
