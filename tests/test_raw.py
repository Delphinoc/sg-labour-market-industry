import hashlib

import pytest

from src.checks import run_checks
from src.config import DATASETS, RAW_DIR

# Totals checked against the data.gov.sg API on 15 Nov 2026 (2006-2025, 13 industries)
API_TOTALS = {
    "incidence": (260, 1638.7, 2),
    "retrenched": (260, 422770.0, 2),
    "vacancy": (260, 2077600.0, 0),
    "resignation": (260, 508.7, 0),
}


@pytest.mark.parametrize("name", list(DATASETS))
def test_raw_matches_api_totals(raw, name):
    import pandas as pd
    col = DATASETS[name]["value_col"]
    n, total, dashes = API_TOTALS[name]
    df = raw[name]
    assert len(df) == n
    assert round(pd.to_numeric(df[col], errors="coerce").sum(), 2) == total
    assert (df[col] == "-").sum() == dashes


def test_no_error_rule_fails(raw):
    failed = [r.rule for r in run_checks(raw) if r.severity == "error" and not r.passed]
    assert failed == []


def test_hierarchy_rule_present(raw):
    rules = [r.rule for r in run_checks(raw)]
    assert sum("reconciles" in r for r in rules) == 2


def test_raw_files_exist_and_nonempty():
    for m in DATASETS.values():
        p = RAW_DIR / m["file"]
        assert p.exists() and len(hashlib.sha256(p.read_bytes()).hexdigest()) == 64
