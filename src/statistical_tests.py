"""Tests estadísticos para rendimiento Manchester United."""

import json
from pathlib import Path

try:
    import numpy as np  # noqa: F401
    import pandas as pd
    from scipy import stats

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


def run_statistical_tests(
    data_dir: Path = Path("."), output_dir: Path = Path("data/export")
) -> dict:
    if not SCIPY_AVAILABLE:
        return {}

    df = pd.read_csv(data_dir / "analisis_united_2014_2024.csv", encoding="utf-8")
    results = {}

    # 1. Paired t-test: Home vs Away points
    if "home_points" in df.columns and "away_points" in df.columns:
        home = df["home_points"].dropna()
        away = df["away_points"].dropna()
        if len(home) > 5:
            t, p = stats.ttest_rel(home, away)
            results["paired_ttest_home_vs_away"] = {
                "test": "Paired t-test",
                "h0": "No diferencia significativa entre puntos en casa y fuera",
                "t_statistic": round(t, 4),
                "p_value": round(p, 6),
                "significant": p < 0.05,
                "home_mean": round(home.mean(), 2),
                "away_mean": round(away.mean(), 2),
            }
            print(f"[STATS] Paired t: t={t:.3f}, p={p:.4f}")

    # 2. Mann-Whitney: Top 6 vs Rest
    if "tier" in df.columns and "points" in df.columns:
        top6 = df[df["tier"] == "Top 6"]["points"].dropna()
        rest = df[df["tier"] == "Rest"]["points"].dropna()
        if len(top6) > 3 and len(rest) > 3:
            u, p_mw = stats.mannwhitneyu(top6, rest, alternative="greater")
            results["mannwhitney_top6_vs_rest"] = {
                "test": "Mann-Whitney U (one-sided)",
                "h0": "Top 6 no tiene más puntos que el resto",
                "u_statistic": round(u, 4),
                "p_value": round(p_mw, 6),
                "significant": p_mw < 0.05,
                "top6_median": round(top6.median(), 2),
                "rest_median": round(rest.median(), 2),
            }
            print(f"[STATS] Mann-Whitney: U={u:.1f}, p={p_mw:.4f}")

    # 3. Pearson: net_spend vs points
    if "net_spend_m" in df.columns and "points" in df.columns:
        valid = df[["net_spend_m", "points"]].dropna()
        if len(valid) > 5:
            r, p_corr = stats.pearsonr(valid["net_spend_m"], valid["points"])
            results["pearson_spend_vs_points"] = {
                "test": "Pearson correlation",
                "h0": "No correlación entre gasto neto y puntos",
                "r": round(r, 4),
                "r_squared": round(r**2, 4),
                "p_value": round(p_corr, 6),
                "significant": p_corr < 0.05,
                "n_observations": len(valid),
            }
            print(f"[STATS] Pearson: r={r:.3f}, p={p_corr:.4f}")

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "statistical_tests.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return results
