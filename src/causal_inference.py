"""
Comparación descriptiva before/after: cambios de entrenador en Manchester United.

Media de puntos en ventanas pre/post de cada cambio + test placebo de cortes
aleatorios.

⚠️ NO es Difference-in-Differences ni identificación causal: no hay grupo de
control ni tendencias paralelas verificables (n de cambios pequeño). Los
resultados son descriptivos de la forma "antes vs después".
"""

import json
from pathlib import Path

try:
    import numpy as np
    import pandas as pd
    from scipy import stats

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def run_causal_analysis(data_dir: Path = Path("."), output_dir: Path = Path("data/export")) -> dict:
    """
    Comparación before/after descriptiva en cambios de entrenador.

    Para cada cambio calcula media de puntos en ventana pre y post
    (sin grupo control: es descriptivo, NO estima un efecto causal).

    Returns:
        dict con diferencias pre/post descriptivas y diagnósticos
    """
    if not PANDAS_AVAILABLE:
        print("[PRE/POST] pandas/statsmodels no instalados")
        return {}

    csv_path = data_dir / "analisis_united_2014_2024.csv"
    if not csv_path.exists():
        csv_path = data_dir.parent / "analisis_united_2014_2024.csv"
    df = pd.read_csv(csv_path, encoding="utf-8")
    # A10: el CSV usa nombres en español; mapear a los esperados por el análisis
    df = df.rename(columns={"entrenador": "manager", "pts_utd": "points", "año": "season"})
    results = {}

    # Identify managerial changes
    if "manager" in df.columns:
        change_points = []
        for i in range(1, len(df)):
            if df.iloc[i]["manager"] != df.iloc[i - 1]["manager"]:
                change_points.append(
                    {
                        "season": int(df.iloc[i]["season"]),
                        "from_manager": str(df.iloc[i - 1]["manager"]),
                        "to_manager": str(df.iloc[i]["manager"]),
                        "index": i,
                    }
                )

        results["managerial_changes"] = change_points
        print(f"[PRE/POST] {len(change_points)} cambios de entrenador detectados")

        # Before/after (pre/post) comparison for each change
        did_results = []
        for cp in change_points:
            idx = cp["index"]
            pre_window = df.iloc[max(0, idx - 3) : idx]
            post_window = df.iloc[idx : min(len(df), idx + 3)]

            if len(pre_window) > 0 and len(post_window) > 0 and "points" in df.columns:
                pre_mean = pre_window["points"].mean()
                post_mean = post_window["points"].mean()

                # Diferencia descriptiva post − pre (sin grupo control)
                delta = post_mean - pre_mean

                # Statistical test
                if len(pre_window) > 2 and len(post_window) > 2:
                    t_stat, p_value = stats.ttest_ind(pre_window["points"], post_window["points"])
                else:
                    t_stat, p_value = 0, 1

                did_results.append(
                    {
                        "change_season": cp["season"],
                        "from": cp["from_manager"],
                        "to": cp["to_manager"],
                        "pre_points_mean": round(pre_mean, 2),
                        "post_points_mean": round(post_mean, 2),
                        "delta_points": round(delta, 2),
                        "t_statistic": round(float(t_stat), 4),
                        "p_value": round(float(p_value), 4),
                        "significant": bool(p_value < 0.05),
                        "direction": "mejora" if delta > 0 else "deterioro",
                    }
                )
                print(
                    f"  {cp['from_manager']} → {cp['to_manager']}: Δ={delta:+.1f} pts (p={p_value:.3f})"
                )

        results["before_after_estimates"] = did_results

        # Resumen descriptivo global (no causal)
        if did_results:
            deltas = [d["delta_points"] for d in did_results]
            sig_changes = [d for d in did_results if d["significant"]]
            results["before_after_summary"] = {
                "n_changes": len(did_results),
                "n_significant": len(sig_changes),
                "mean_delta": round(np.mean(deltas), 2),
                "median_delta": round(np.median(deltas), 2),
                "best_change": max(did_results, key=lambda x: x["delta_points"])
                if did_results
                else None,
                "worst_change": min(did_results, key=lambda x: x["delta_points"])
                if did_results
                else None,
                "note": "Descriptivo before/after sin grupo control — no es un efecto causal",
            }

    # Proyección de tendencia lineal descriptiva (no contrafactual causal)
    if "points" in df.columns and len(df) >= 5:
        overall_trend = np.polyfit(range(len(df)), df["points"].fillna(0).values, 1)
        counterfactual_2025 = np.polyval(overall_trend, len(df))

        results["trend_projection"] = {
            "trend_slope": round(overall_trend[0], 3),
            "projected_2025_points": round(counterfactual_2025, 1),
            "actual_2025_points": round(float(df["points"].iloc[-1]), 1)
            if pd.notna(df["points"].iloc[-1])
            else None,
            "interpretation": "La tendencia sugiere mejora/deterioro"
            if abs(overall_trend[0]) > 0.5
            else "Tendencia estable",
        }

    # Placebo test: random assignment
    if "points" in df.columns:
        real_delta = (
            results.get("before_after_estimates", [{}])[0].get("delta_points", 0)
            if results.get("before_after_estimates")
            else 0
        )
        placebo_deltas = []
        for _ in range(1000):
            random_idx = np.random.randint(1, len(df) - 1)
            pre = df.iloc[max(0, random_idx - 3) : random_idx]["points"].dropna()
            post = df.iloc[random_idx : min(len(df), random_idx + 3)]["points"].dropna()
            if len(pre) > 0 and len(post) > 0:
                placebo_deltas.append(post.mean() - pre.mean())

        if placebo_deltas:
            p_placebo = np.mean([abs(a) >= abs(real_delta) for a in placebo_deltas])
            results["placebo_test"] = {
                "n_simulations": 1000,
                "p_value_placebo": round(float(p_placebo), 4),
                "significant": bool(p_placebo < 0.05),
                "interpretation": "Δ pre/post mayor que el 95% de cortes aleatorios (descriptivo, no causal)"
                if p_placebo < 0.05
                else "Δ pre/post no se distingue de cortes aleatorios (descriptivo)",
            }
            print(f"[PRE/POST] Placebo test: p={p_placebo:.4f}")

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "before_after_analysis.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return results


if __name__ == "__main__":
    run_causal_analysis()
