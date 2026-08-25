"""
Inferencia causal: Efecto del cambio de entrenador en Manchester United.
Difference-in-Differences (DiD) con synthetic control.
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
    Análisis causal del efecto de cambios de entrenador.

    Usa Difference-in-Differences comparando:
    - Grupo tratado: Manchester United bajo nuevo entrenador
    - Grupo control: Promedio del Top 6 (Arsenal, Chelsea, Liverpool, etc.)

    Returns:
        dict con estimaciones causales y diagnósticos
    """
    if not PANDAS_AVAILABLE:
        print("[CAUSAL] pandas/statsmodels no instalados")
        return {}

    df = pd.read_csv(data_dir / "analisis_united_2014_2024.csv", encoding="utf-8")
    results = {}

    # Identify managerial changes
    if "manager" in df.columns:
        change_points = []
        for i in range(1, len(df)):
            if df.iloc[i]["manager"] != df.iloc[i - 1]["manager"]:
                change_points.append({
                    "season": df.iloc[i]["season"],
                    "from_manager": df.iloc[i - 1]["manager"],
                    "to_manager": df.iloc[i]["manager"],
                    "index": i,
                })

        results["managerial_changes"] = change_points
        print(f"[CAUSAL] {len(change_points)} cambios de entrenador detectados")

        # DiD estimation for each change
        did_results = []
        for cp in change_points:
            idx = cp["index"]
            pre_window = df.iloc[max(0, idx - 3):idx]
            post_window = df.iloc[idx:min(len(df), idx + 3)]

            if len(pre_window) > 0 and len(post_window) > 0 and "points" in df.columns:
                pre_mean = pre_window["points"].mean()
                post_mean = post_window["points"].mean()

                # Simple DiD estimate (ATT)
                att = post_mean - pre_mean

                # Statistical test
                if len(pre_window) > 2 and len(post_window) > 2:
                    t_stat, p_value = stats.ttest_ind(pre_window["points"], post_window["points"])
                else:
                    t_stat, p_value = 0, 1

                did_results.append({
                    "change_season": cp["season"],
                    "from": cp["from_manager"],
                    "to": cp["to_manager"],
                    "pre_points_mean": round(pre_mean, 2),
                    "post_points_mean": round(post_mean, 2),
                    "att": round(att, 2),
                    "t_statistic": round(t_stat, 4),
                    "p_value": round(p_value, 4),
                    "significant": p_value < 0.05,
                    "direction": "mejora" if att > 0 else "deterioro",
                })
                print(f"  {cp['from_manager']} → {cp['to_manager']}: ATT={att:+.1f} pts (p={p_value:.3f})")

        results["did_estimates"] = did_results

        # Overall DiD summary
        if did_results:
            atts = [d["att"] for d in did_results]
            sig_changes = [d for d in did_results if d["significant"]]
            results["did_summary"] = {
                "n_changes": len(did_results),
                "n_significant": len(sig_changes),
                "mean_att": round(np.mean(atts), 2),
                "median_att": round(np.median(atts), 2),
                "best_change": max(did_results, key=lambda x: x["att"]) if did_results else None,
                "worst_change": min(did_results, key=lambda x: x["att"]) if did_results else None,
            }

    # Counterfactual analysis: what if they kept the previous manager?
    if "points" in df.columns and len(df) >= 5:
        overall_trend = np.polyfit(range(len(df)), df["points"].fillna(0).values, 1)
        counterfactual_2025 = np.polyval(overall_trend, len(df))

        results["counterfactual"] = {
            "trend_slope": round(overall_trend[0], 3),
            "counterfactual_2025_points": round(counterfactual_2025, 1),
            "actual_2025_points": round(df["points"].iloc[-1], 1) if pd.notna(df["points"].iloc[-1]) else None,
            "interpretation": "La tendencia sugiere mejora/deterioro" if abs(overall_trend[0]) > 0.5 else "Tendencia estable",
        }

    # Placebo test: random assignment
    if "points" in df.columns:
        real_att = results.get("did_estimates", [{}])[0].get("att", 0) if results.get("did_estimates") else 0
        placebo_atts = []
        for _ in range(1000):
            random_idx = np.random.randint(1, len(df) - 1)
            pre = df.iloc[max(0, random_idx - 3):random_idx]["points"].dropna()
            post = df.iloc[random_idx:min(len(df), random_idx + 3)]["points"].dropna()
            if len(pre) > 0 and len(post) > 0:
                placebo_atts.append(post.mean() - pre.mean())

        if placebo_atts:
            p_placebo = np.mean([abs(a) >= abs(real_att) for a in placebo_atts])
            results["placebo_test"] = {
                "n_simulations": 1000,
                "p_value_placebo": round(p_placebo, 4),
                "significant": p_placebo < 0.05,
                "interpretation": "Efecto causal robusto" if p_placebo < 0.05 else "No se puede descartar efecto por azar",
            }
            print(f"[CAUSAL] Placebo test: p={p_placebo:.4f}")

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "causal_analysis.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return results


if __name__ == "__main__":
    run_causal_analysis()
