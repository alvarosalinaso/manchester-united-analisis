"""Tests estadisticos para rendimiento Manchester United."""

import json
from pathlib import Path

try:
    import numpy as np
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

    csv_path = data_dir / "analisis_united_2014_2024.csv"
    if not csv_path.exists():
        csv_path = data_dir.parent / "analisis_united_2014_2024.csv"
    df = pd.read_csv(csv_path, encoding="utf-8")
    results = {}

    # 1. Pearson: brecha de puntos vs brecha de ataque
    valid = df[["brecha_puntos", "brecha_ataque"]].dropna()
    if len(valid) > 5:
        r, p = stats.pearsonr(valid["brecha_puntos"], valid["brecha_ataque"])
        results["pearson_brecha_puntos_vs_ataque"] = {
            "test": "Pearson correlation",
            "h0": "No correlacion entre brecha de puntos y brecha de ataque",
            "r": round(r, 4),
            "r_squared": round(r**2, 4),
            "p_value": round(p, 6),
            "significant": p < 0.05,
            "n_observations": len(valid),
        }
        print(f"[STATS] Pearson brecha: r={r:.3f}, p={p:.4f}")

    # 2. T-test: temporada de transicion vs normal
    transicion = df[df["es_transicion"] == True]["pts_utd"].dropna()  # noqa: E712
    normal = df[df["es_transicion"] == False]["pts_utd"].dropna()  # noqa: E712
    if len(transicion) > 2 and len(normal) > 2:
        t, p = stats.ttest_ind(transicion, normal, equal_var=False)
        results["ttest_transicion_vs_normal"] = {
            "test": "Welch's t-test",
            "h0": "No hay diferencia de puntos entre temporadas de transicion y normales",
            "t_statistic": round(t, 4),
            "p_value": round(p, 6),
            "significant": p < 0.05,
            "transicion_mean": round(transicion.mean(), 2),
            "normal_mean": round(normal.mean(), 2),
        }
        print(f"[STATS] t-test transicion: t={t:.3f}, p={p:.4f}")

    # 3. Mann-Whitney: top 4 vs resto
    top4 = df[df["pos_utd"] <= 4]["pts_utd"].dropna()
    resto = df[df["pos_utd"] > 4]["pts_utd"].dropna()
    if len(top4) > 2 and len(resto) > 2:
        u, p_mw = stats.mannwhitneyu(top4, resto, alternative="greater")
        results["mannwhitney_top4_vs_resto"] = {
            "test": "Mann-Whitney U",
            "h0": "Top 4 no tiene mas puntos que el resto",
            "u_statistic": round(u, 4),
            "p_value": round(p_mw, 6),
            "significant": p_mw < 0.05,
            "top4_median": round(top4.median(), 2),
            "resto_median": round(resto.median(), 2),
        }
        print(f"[STATS] Mann-Whitney: U={u:.1f}, p={p_mw:.4f}")

    # 4. Pearson: pts_por_gol vs posicion
    valid2 = df[["pts_por_gol", "pos_utd"]].dropna()
    if len(valid2) > 5:
        r2, p2 = stats.pearsonr(valid2["pts_por_gol"], valid2["pos_utd"])
        results["pearson_eficiencia_vs_posicion"] = {
            "test": "Pearson correlation",
            "h0": "No correlacion entre eficiencia (pts/gol) y posicion final",
            "r": round(r2, 4),
            "r_squared": round(r2**2, 4),
            "p_value": round(p2, 6),
            "significant": p2 < 0.05,
            "n_observations": len(valid2),
        }
        print(f"[STATS] Pearson eficiencia: r={r2:.3f}, p={p2:.4f}")

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "statistical_tests.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return results
