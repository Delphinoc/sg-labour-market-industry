"""Static charts and a one-page dashboard image from the processed marts."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import pandas as pd

from src.config import OUTPUT_DIR, PROCESSED_DIR

INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#a3a29b", "#e6e5e0", "#fcfcfb"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
SEG_COLORS = {"Restructuring": BLUE, "Churn": ORANGE, "Tight": AQUA, "Stable": YELLOW}
SHORT = {
    "information and communications": "ICT", "financial and insurance services": "Finance & insurance",
    "wholesale and retail trade": "Wholesale & retail", "professional services": "Professional svcs",
    "manufacturing": "Manufacturing", "transportation and storage": "Transport & storage",
    "administrative and support services": "Admin & support", "real estate services": "Real estate",
    "construction": "Construction", "accommodation and food services": "Accommodation & F&B",
    "community, social and personal services": "Community & social", "services": "All services",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.titlecolor": INK,
    "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
})


def _load():
    v = pd.read_csv(PROCESSED_DIR / "v_industry_year.csv")
    seg = pd.read_csv(PROCESSED_DIR / "mart_industry_segments.csv")
    eco = pd.read_csv(PROCESSED_DIR / "mart_economy_trend.csv")
    return v, seg, eco


def ict_trend(ax, v):
    inc = v.pivot(index="year", columns="industry", values="retrench_per_1000")
    others = [c for c in inc.columns if c not in ("information and communications", "services", "others")]
    for c in others:
        ax.plot(inc.index, inc[c], color=MUTED, lw=1, alpha=0.6)
    ax.plot(inc.index, inc["information and communications"], color=BLUE, lw=2.2)
    ax.plot(inc.index, inc["services"], color=INK2, lw=2, ls="--")
    ax.annotate("ICT", (2025, inc.loc[2025, "information and communications"]), xytext=(4, 0),
                textcoords="offset points", color=INK, fontweight="bold", va="center")
    ax.annotate("All services", (2025, inc.loc[2025, "services"]), xytext=(4, 0),
                textcoords="offset points", color=INK2, va="center")
    ax.axvspan(2023, 2025, color=BLUE, alpha=0.06, lw=0)
    ax.set_title("ICT retrenchment incidence has stayed high since 2023")
    ax.set_ylabel("Retrenched per 1,000 employees")
    ax.set_xlim(2006, 2027.5)
    ax.text(0, -0.16, "Grey lines: other industries. Shaded: 2023–25.", transform=ax.transAxes, color=INK2, fontsize=8)


def segments(ax, seg):
    for _, r in seg.iterrows():
        key = r.segment.split(":")[0]
        ax.scatter(r.incidence_latest, r.vpr_latest, s=70, color=SEG_COLORS[key], edgecolor=SURFACE, lw=2, zorder=3)
        off = {"wholesale and retail trade": (0, -13), "financial and insurance services": (6, 6),
               "manufacturing": (-8, 4)}.get(r.industry, (6, 3))
        ax.annotate(SHORT.get(r.industry, r.industry), (r.incidence_latest, r.vpr_latest), xytext=off,
                    textcoords="offset points", fontsize=8, color=INK, ha="right" if off[0] < 0 else "left")
    ax.axvline(seg.incidence_latest.median(), color=MUTED, lw=1, ls=":")
    ax.axhline(seg.vpr_latest.median(), color=MUTED, lw=1, ls=":")
    ax.set_yscale("log")
    ax.set_yticks([2, 5, 10, 20, 50]); ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%g"))
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); ax.set_ylim(1.8, 70)
    ax.set_xlabel("Retrenched per 1,000 employees (avg 2023–25)")
    ax.set_ylabel("Vacancies per retrenched worker (log)")
    ax.set_title("Where job losses sit against open vacancies, 2023–25")
    handles = [plt.Line2D([], [], marker="o", ls="", color=c, markersize=8, label=k) for k, c in SEG_COLORS.items()
               if k in set(seg.segment.str.split(":").str[0])]
    ax.legend(handles=handles, frameon=False, fontsize=8, loc="upper right")
    ax.set_xlim(0, 23)


def economy(ax, eco):
    ax.plot(eco.year, eco.vacancies_per_retrenched, color=BLUE, lw=2, marker="o", markersize=4)
    for y in (2009, 2020, 2022, 2025):
        val = eco.set_index("year").loc[y, "vacancies_per_retrenched"]
        ax.annotate(f"{val:.1f}", (y, val), xytext=(0, -14 if y in (2009, 2020) else 7), textcoords="offset points", ha="center", fontsize=8, color=INK)
    ax.set_title("Vacancies per retrenched worker, whole economy")
    ax.set_ylabel("Ratio")
    ax.set_ylim(0, 20)


def resignations(ax, v):
    r = v.pivot(index="year", columns="industry", values="resignation_rate_pct")
    for c, col, lab in [("services", BLUE, "Services"), ("construction", ORANGE, "Construction"),
                        ("manufacturing", AQUA, "Manufacturing")]:
        ax.plot(r.index, r[c], color=col, lw=2, label=lab)
        ax.annotate(lab, (2025, r.loc[2025, c]), xytext=(4, 0), textcoords="offset points", fontsize=8, color=INK, va="center")
    ax.set_title("Resignation rates at their lowest since 2006")
    ax.set_ylabel("Avg monthly resignation rate (%)")
    ax.set_ylim(0, 2.6)
    ax.set_xlim(2006, 2028)
    ax.legend(frameon=False, fontsize=8, loc="lower left")


def _years(ax):
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(4))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%d"))


def main() -> None:
    v, seg, eco = _load()
    (OUTPUT_DIR / "charts").mkdir(parents=True, exist_ok=True)
    for name, fn, data in [("ict_retrenchment_trend", ict_trend, v), ("industry_segments", segments, seg),
                           ("vacancies_per_retrenched", economy, eco), ("resignation_trend", resignations, v)]:
        fig, ax = plt.subplots(figsize=(7.5, 4.6))
        fn(ax, data)
        if fn is not segments: _years(ax)
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / "charts" / f"{name}.png", dpi=160)
        plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(15, 9.5))
    ict_trend(axes[0, 0], v); segments(axes[0, 1], seg); economy(axes[1, 0], eco); resignations(axes[1, 1], v)
    for a in (axes[0, 0], axes[1, 0], axes[1, 1]): _years(a)
    fig.suptitle("Singapore labour market by industry, 2006–2025", x=0.01, ha="left", fontsize=16, fontweight="bold", color=INK)
    fig.text(0.01, 0.005, "Source: Ministry of Manpower, Labour Market Survey (data.gov.sg, Singapore Open Data Licence). "
             "Counts rounded by MOM. 2023–25 vs 2015–19 averages.", fontsize=8, color=INK2)
    fig.tight_layout(rect=(0, 0.02, 1, 0.96))
    fig.savefig(OUTPUT_DIR / "dashboard.png", dpi=130)
    plt.close(fig)
    print("charts written")


if __name__ == "__main__":
    main()
