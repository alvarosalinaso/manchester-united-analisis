"""
Análisis de cohortes y retención — Manchester United.
Analiza retención de jugadores y estabilidad de plantillas por era de entrenador.
"""
import json
from pathlib import Path

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def run_cohort_analysis(data_dir: Path = Path("."), output_dir: Path = Path("data/export")) -> dict:
    """
    Análisis de cohortes por era de entrenador.

    Cohorts: cada entrenador define una cohorte
    Métricas: retención de jugadores, rendimiento acumulado, estabilidad

    Returns:
        dict con análisis de cohortes y retención
    """
    if not PANDAS_AVAILABLE:
        print("[COHORT] pandas no instalado")
        return {}

    df = pd.read_csv(data_dir / "analisis_united_2014_2024.csv", encoding="utf-8")
    results = {}

    if "manager" not in df.columns:
        print("[COHORT] Columna 'manager' no encontrada")
        return {}

    # Define manager eras (cohorts)
    managers = df["manager"].dropna().unique()

    cohort_data = []
    for mgr in managers:
        mgr_df = df[df["manager"] == mgr]
        if len(mgr_df) == 0:
            continue

        tenure_seasons = len(mgr_df)

        cohort = {
            "manager": mgr,
            "tenure_seasons": tenure_seasons,
            "seasons_range": f"{mgr_df['season'].iloc[0]} - {mgr_df['season'].iloc[-1]}" if "season" in mgr_df.columns else "N/A",
        }

        # Performance metrics
        if "points" in mgr_df.columns:
            cohort["avg_points"] = round(mgr_df["points"].mean(), 2)
            cohort["total_points"] = int(mgr_df["points"].sum())
            cohort["best_season_points"] = int(mgr_df["points"].max())
            cohort["worst_season_points"] = int(mgr_df["points"].min())
            cohort["points_std"] = round(mgr_df["points"].std(), 2)

        if "position" in mgr_df.columns:
            cohort["avg_position"] = round(mgr_df["position"].mean(), 1)
            cohort["best_position"] = int(mgr_df["position"].min())

        # Retention metric: consistency (lower std = more stable)
        if "points_std" in cohort:
            cohort["stability_score"] = round(1 / (1 + cohort["points_std"]), 3)

        cohort_data.append(cohort)

    # Sort by tenure
    cohort_data.sort(key=lambda x: x["tenure_seasons"], reverse=True)

    results["manager_cohorts"] = cohort_data

    # Retention analysis: who stayed longest?
    if cohort_data:
        longest = max(cohort_data, key=lambda x: x["tenure_seasons"])
        best = max(cohort_data, key=lambda x: x.get("avg_points", 0))
        most_stable = max(cohort_data, key=lambda x: x.get("stability_score", 0))

        results["retention_summary"] = {
            "longest_tenure": {"manager": longest["manager"], "seasons": longest["tenure_seasons"]},
            "best_performance": {"manager": best["manager"], "avg_points": best.get("avg_points", 0)},
            "most_stable": {"manager": most_stable["manager"], "stability": most_stable.get("stability_score", 0)},
            "n_managers": len(cohort_data),
            "avg_tenure": round(np.mean([c["tenure_seasons"] for c in cohort_data]), 1),
            "avg_tenure_industry": 2.5,  # Industry average
            "turnover_rate": round(len(cohort_data) / 10, 2),  # managers per decade
        }

    # Season-over-season retention (performance trajectory)
    if "points" in df.columns and "season" in df.columns:
        df_sorted = df.sort_values("season")
        df_sorted["points_change"] = df_sorted["points"].diff()
        df_sorted["points_pct_change"] = df_sorted["points"].pct_change()

        # Identify manager transition effects
        transitions = []
        for i in range(1, len(df_sorted)):
            if df_sorted.iloc[i]["manager"] != df_sorted.iloc[i-1]["manager"]:
                transitions.append({
                    "season": df_sorted.iloc[i]["season"],
                    "from": df_sorted.iloc[i-1]["manager"],
                    "to": df_sorted.iloc[i]["manager"],
                    "points_before": int(df_sorted.iloc[i-1]["points"]) if pd.notna(df_sorted.iloc[i-1]["points"]) else None,
                    "points_after": int(df_sorted.iloc[i]["points"]) if pd.notna(df_sorted.iloc[i]["points"]) else None,
                    "change": round(df_sorted.iloc[i]["points"] - df_sorted.iloc[i-1]["points"], 2) if pd.notna(df_sorted.iloc[i]["points"]) and pd.notna(df_sorted.iloc[i-1]["points"]) else None,
                })

        results["managerial_transitions"] = transitions

        # Transition success rate
        valid_transitions = [t for t in transitions if t["change"] is not None]
        improvements = [t for t in valid_transitions if t["change"] > 0]
        results["transition_analysis"] = {
            "total_transitions": len(transitions),
            "improvements": len(improvements),
            "declines": len(valid_transitions) - len(improvements),
            "improvement_rate": round(len(improvements) / len(valid_transitions) * 100, 1) if valid_transitions else 0,
            "avg_change": round(np.mean([t["change"] for t in valid_transitions]), 2) if valid_transitions else 0,
        }
        print(f"[COHORT] {len(transitions)} transiciones, {len(improvements)} mejoras ({results['transition_analysis']['improvement_rate']}%)")

    # Save
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "cohort_analysis.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    if cohort_data:
        print(f"[COHORT] {len(cohort_data)} cohortes analizadas")
        for c in cohort_data[:3]:
            print(f"  {c['manager']}: {c['tenure_seasons']} temporadas, {c.get('avg_points', 'N/A')} pts promedio")

    return results


if __name__ == "__main__":
    run_cohort_analysis()
