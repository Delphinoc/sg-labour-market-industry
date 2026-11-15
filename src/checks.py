"""Data-quality rules run on the raw MOM files before modelling.

Errors stop the pipeline; warnings are logged for review.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.config import DATASETS, FIRST_YEAR, INDUSTRIES, LAST_YEAR, ROUNDING, SERVICE_SUBS


@dataclass
class Result:
    rule: str
    severity: str  # "error" or "warning"
    passed: bool
    detail: str = ""


def _num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.replace("-", pd.NA), errors="coerce")


def run_checks(raw: dict[str, pd.DataFrame]) -> list[Result]:
    out: list[Result] = []
    years = set(range(FIRST_YEAR, LAST_YEAR + 1))

    for name, df in raw.items():
        col = DATASETS[name]["value_col"]
        # 1. Known industries only
        unknown = set(df["industry"]) - set(INDUSTRIES)
        out.append(Result(f"{name}: industries known", "error", not unknown, str(sorted(unknown))))
        # 2. Full grid: every industry x year, no duplicates
        dup = df.duplicated(["year", "industry"]).sum()
        missing = len(years) * len(INDUSTRIES) - len(df.drop_duplicates(["year", "industry"]))
        out.append(Result(f"{name}: one row per industry x year, full grid", "error", dup == 0 and missing == 0,
                          f"duplicates={dup}, missing={missing}"))
        # 3. Values numeric or '-' only
        bad = df[_num(df[col]).isna() & (df[col].astype(str) != "-")]
        out.append(Result(f"{name}: values numeric or '-'", "error", bad.empty, f"{len(bad)} bad values"))
        # 4. Non-negative
        neg = (_num(df[col]) < 0).sum()
        out.append(Result(f"{name}: non-negative", "error", neg == 0, f"{neg} negative"))
        # 5. '-' entries logged (nil or negligible)
        dashes = (df[col].astype(str) == "-").sum()
        out.append(Result(f"{name}: nil/negligible ('-') entries", "warning", dashes == 0, f"{dashes} entries"))

    # 6. Rates within plausible bounds
    inc = _num(raw["incidence"]["incidence_of_retrenchment"])
    out.append(Result("incidence within 0-1000 per 1,000", "error", bool(inc.dropna().between(0, 1000).all())))
    res = _num(raw["resignation"]["resignation_rate"])
    out.append(Result("resignation rate within 0-100%", "error", bool(res.dropna().between(0, 100).all())))

    # 7. Hierarchy: services = sum of its sub-industries, within MOM rounding
    for name, step in ROUNDING.items():
        col = DATASETS[name]["value_col"]
        df = raw[name].assign(v=_num(raw[name][col]))
        p = df.pivot(index="year", columns="industry", values="v")
        gap = (p["services"] - p[SERVICE_SUBS].sum(axis=1)).abs()
        tol = step / 2 * (len(SERVICE_SUBS) + 1)
        worst = gap.max()
        out.append(Result(f"{name}: services reconciles to sub-industries (tol {tol:.0f})", "error",
                          bool((gap <= tol).all()), f"max gap {worst:.0f}"))

    # 8. Retrenched count and incidence agree on zero vs non-zero
    m = raw["retrenched"].merge(raw["incidence"], on=["year", "industry"])
    r, i = _num(m["retrench"]), _num(m["incidence_of_retrenchment"])
    mismatch = ((r.isna() | (r == 0)) != (i.isna() | (i == 0))).sum()
    out.append(Result("retrenched count and incidence agree on nil", "error", mismatch == 0, f"{mismatch} rows"))

    # 9. Large year-on-year swings in retrenchment incidence (flag, don't stop)
    w = raw["incidence"].assign(v=inc).sort_values(["industry", "year"])
    w["chg"] = w.groupby("industry")["v"].diff().abs()
    swings = w[w["chg"] > 10]
    out.append(Result("incidence YoY swing <= 10 per 1,000", "warning", swings.empty,
                      f"{len(swings)} swings, e.g. " + ", ".join(f"{a} {b}" for a, b in swings[['industry','year']].head(4).values)))
    return out
