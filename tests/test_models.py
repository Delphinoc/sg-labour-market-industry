import pandas as pd


def q(con, sql):
    return con.execute(sql).df()


def test_dim_keys_unique(con):
    assert q(con, "SELECT COUNT(*) n, COUNT(DISTINCT industry_key) k FROM dim_industry").eval("n == k").all()
    assert q(con, "SELECT COUNT(*) n, COUNT(DISTINCT year_key) k FROM dim_year").eval("n == k").all()


def test_fact_grain_and_no_orphans(con):
    d = q(con, "SELECT COUNT(*) n, COUNT(DISTINCT (industry_key, year_key)) g FROM fct_industry_year")
    assert d.n[0] == d.g[0] == 13 * 20
    orphans = q(con, """SELECT COUNT(*) n FROM fct_industry_year f
                        LEFT JOIN dim_industry d USING (industry_key)
                        LEFT JOIN dim_year y USING (year_key)
                        WHERE d.industry IS NULL OR y.year IS NULL""")
    assert orphans.n[0] == 0


def test_fact_reconciles_to_staging(con):
    stg = q(con, "SELECT measure, SUM(value) s FROM stg_labour GROUP BY measure").set_index("measure").s
    f = q(con, """SELECT SUM(retrench_per_1000) incidence, SUM(retrenched) retrenched,
                         SUM(vacancies) vacancy, SUM(resignation_rate_pct) resignation FROM fct_industry_year""").iloc[0]
    for k in stg.index:
        assert abs(stg[k] - f[k]) < 1e-6


def test_economy_total_matches_level1_sum(con):
    eco = q(con, "SELECT * FROM mart_economy_trend").set_index("year")
    v = q(con, "SELECT * FROM v_industry_year")
    lvl1 = v[v.industry.isin(["manufacturing", "construction", "services", "others"])].groupby("year").retrenched.sum()
    assert (eco.retrenched - lvl1).abs().max() == 0


def test_period_compare_independent_pandas(con, raw):
    """Rebuild the ICT 2015-19 vs 2023-25 incidence averages in pandas."""
    inc = raw["incidence"].copy()
    inc["v"] = pd.to_numeric(inc["incidence_of_retrenchment"], errors="coerce")
    ict = inc[inc.industry == "information and communications"].set_index("year").v
    m = q(con, "SELECT * FROM mart_period_compare WHERE industry = 'information and communications'").iloc[0]
    assert m.incidence_base == round(ict.loc[2015:2019].mean(), 1) == 11.3
    assert m.incidence_latest == round(ict.loc[2023:2025].mean(), 1) == 20.1


def test_segments_cover_11_industries(con):
    s = q(con, "SELECT * FROM mart_industry_segments")
    assert len(s) == 11 and s.industry.is_unique
    assert s.set_index("industry").loc["information and communications", "segment"].startswith("Restructuring")


def test_headline_findings(con):
    eco = q(con, "SELECT * FROM mart_economy_trend").set_index("year").vacancies_per_retrenched
    assert eco.idxmax() == 2022 and eco.max() == 17.8
    res = q(con, "SELECT industry, year, resignation_rate_pct r FROM v_industry_year")
    lows = res.loc[res.groupby("industry").r.idxmin()]
    # every industry's lowest resignation rate (ties included) occurs in 2025
    assert all(res[(res.industry == i) & (res.year == 2025)].r.iloc[0] == res[res.industry == i].r.min()
               for i in res.industry.unique())
