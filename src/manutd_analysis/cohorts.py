"""Análisis de cohortes por era de entrenador (tenencia, rendimiento, estabilidad).

No hay datos de jugadores, por lo que no se analiza retención de plantel.
"""

from __future__ import annotations

import logging

import pandas as pd

from manutd_analysis.metrics import safe_divide
from manutd_analysis.validator import validate_season_kpis

logger = logging.getLogger(__name__)


def manager_cohorts(kpis: pd.DataFrame) -> pd.DataFrame:
    """Una fila por entrenador (cohorte) con métricas de rendimiento y estabilidad.

    ``stability_score = 1 / (1 + desviación estándar de puntos)``; solo se
    calcula para cohortes con al menos dos temporadas (con una sola la
    desviación no está definida).

    Returns
    -------
    pd.DataFrame
        Ordenado por tenencia descendente.
    """
    validate_season_kpis(kpis)
    ordered = kpis.sort_values("año")
    grouped = ordered.groupby("entrenador", sort=False)
    cohorts = grouped.agg(
        tenure_seasons=("año", "count"),
        first_season=("año", "min"),
        last_season=("año", "max"),
        avg_points=("pts_utd", "mean"),
        total_points=("pts_utd", "sum"),
        best_season_points=("pts_utd", "max"),
        worst_season_points=("pts_utd", "min"),
        points_std=("pts_utd", "std"),
        avg_position=("pos_utd", "mean"),
        best_position=("pos_utd", "min"),
    ).reset_index(names="manager")
    cohorts["stability_score"] = safe_divide(
        pd.Series(1.0, index=cohorts.index), 1 + cohorts["points_std"]
    )
    cohorts = cohorts.round(
        {"avg_points": 2, "points_std": 2, "avg_position": 1, "stability_score": 3}
    )
    return cohorts.sort_values(
        ["tenure_seasons", "first_season"], ascending=[False, True]
    ).reset_index(drop=True)


def cohort_analysis(kpis: pd.DataFrame) -> dict:
    """Resumen de cohortes y de transiciones entre entrenadores.

    Returns
    -------
    dict
        ``manager_cohorts``, ``tenure_summary``, ``managerial_transitions`` y
        ``transition_analysis``.
    """
    cohorts = manager_cohorts(kpis)
    ordered = kpis.sort_values("año").reset_index(drop=True)
    n_seasons = len(ordered)

    multi = cohorts[cohorts["tenure_seasons"] >= 2]
    most_stable = multi.loc[multi["stability_score"].idxmax()] if not multi.empty else None
    longest = cohorts.iloc[0]
    best = cohorts.loc[cohorts["avg_points"].idxmax()]

    summary = {
        "longest_tenure": {
            "manager": longest["manager"],
            "seasons": int(longest["tenure_seasons"]),
        },
        "best_performance": {"manager": best["manager"], "avg_points": float(best["avg_points"])},
        "most_stable": (
            {"manager": most_stable["manager"], "stability": float(most_stable["stability_score"])}
            if most_stable is not None
            else None
        ),
        "n_managers": int(len(cohorts)),
        "avg_tenure": round(float(cohorts["tenure_seasons"].mean()), 1),
        "turnover_rate": round(len(cohorts) / n_seasons * 10, 2) if n_seasons else None,
        "turnover_rate_unit": "entrenadores por cada 10 temporadas",
    }

    previous = ordered.shift(1)
    changed = previous["entrenador"].notna() & (ordered["entrenador"] != previous["entrenador"])
    transitions = pd.DataFrame(
        {
            "season": ordered.loc[changed, "año"].astype(int),
            "from": previous.loc[changed, "entrenador"],
            "to": ordered.loc[changed, "entrenador"],
            "points_before": previous.loc[changed, "pts_utd"].astype(int),
            "points_after": ordered.loc[changed, "pts_utd"].astype(int),
        }
    )
    transitions["change"] = transitions["points_after"] - transitions["points_before"]
    n_trans = len(transitions)
    improvements = int((transitions["change"] > 0).sum())
    transition_analysis = {
        "total_transitions": n_trans,
        "improvements": improvements,
        "declines": n_trans - improvements,
        "improvement_rate": round(improvements / n_trans * 100, 1) if n_trans else None,
        "avg_change": round(float(transitions["change"].mean()), 2) if n_trans else None,
    }
    logger.info(
        "[COHORT] %d cohortes, %d transiciones, %d mejoras", len(cohorts), n_trans, improvements
    )
    return {
        "manager_cohorts": cohorts.to_dict(orient="records"),
        "tenure_summary": summary,
        "managerial_transitions": transitions.to_dict(orient="records"),
        "transition_analysis": transition_analysis,
    }
