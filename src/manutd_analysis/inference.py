"""Inferencia estadística sobre los KPIs por temporada.

Incluye contrastes clásicos (Pearson, Welch, Mann-Whitney) y una comparación
descriptiva pre/post de cada cambio de entrenador con un test placebo de cortes
aleatorios.

.. warning::
   La comparación pre/post **no** es Difference-in-Differences ni una
   estimación causal: no hay grupo de control ni tendencias paralelas
   verificables y el número de cambios es pequeño. Se reporta como evidencia
   descriptiva.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from scipy import stats

from manutd_analysis.config import (
    ALPHA,
    PLACEBO_SEED,
    PLACEBO_SIMULATIONS,
    PRE_POST_WINDOW,
)
from manutd_analysis.validator import validate_season_kpis

logger = logging.getLogger(__name__)

_MIN_OBS_CORRELATION = 6
_MIN_OBS_GROUP = 3


def _pearson(x: pd.Series, y: pd.Series, h0: str) -> dict | None:
    valid = pd.concat([x, y], axis=1).dropna()
    if len(valid) < _MIN_OBS_CORRELATION:
        return None
    r, p = stats.pearsonr(valid.iloc[:, 0], valid.iloc[:, 1])
    return {
        "test": "Pearson correlation",
        "h0": h0,
        "r": round(float(r), 4),
        "r_squared": round(float(r) ** 2, 4),
        "p_value": round(float(p), 6),
        "significant": bool(p < ALPHA),
        "n_observations": int(len(valid)),
    }


def statistical_tests(kpis: pd.DataFrame) -> dict:
    """Ejecuta la batería de contrastes sobre la tabla de KPIs.

    Parameters
    ----------
    kpis : pd.DataFrame
        Tabla de :func:`manutd_analysis.metrics.build_season_kpis`.

    Returns
    -------
    dict
        Un bloque por test con estadístico, ``p_value`` y ``significant``
        (α = 0.05). Los tests sin observaciones suficientes se omiten.
    """
    validate_season_kpis(kpis)
    results: dict = {}

    pearson_gap = _pearson(
        kpis["brecha_puntos"],
        kpis["brecha_ataque"],
        "No hay correlación entre brecha de puntos y brecha de ataque",
    )
    if pearson_gap:
        results["pearson_brecha_puntos_vs_ataque"] = pearson_gap

    transition = kpis.loc[kpis["es_transicion"], "pts_utd"].dropna()
    stable = kpis.loc[~kpis["es_transicion"], "pts_utd"].dropna()
    if len(transition) >= _MIN_OBS_GROUP and len(stable) >= _MIN_OBS_GROUP:
        t, p = stats.ttest_ind(transition, stable, equal_var=False)
        results["ttest_transicion_vs_normal"] = {
            "test": "Welch's t-test",
            "h0": "No hay diferencia de puntos entre temporadas de transición y normales",
            "t_statistic": round(float(t), 4),
            "p_value": round(float(p), 6),
            "significant": bool(p < ALPHA),
            "transicion_mean": round(float(transition.mean()), 2),
            "normal_mean": round(float(stable.mean()), 2),
        }
    else:
        logger.info(
            "Welch omitido: %d temporadas de transición (mínimo %d)",
            len(transition),
            _MIN_OBS_GROUP,
        )

    top4 = kpis.loc[kpis["pos_utd"] <= 4, "pts_utd"].dropna()
    rest = kpis.loc[kpis["pos_utd"] > 4, "pts_utd"].dropna()
    if len(top4) >= _MIN_OBS_GROUP and len(rest) >= _MIN_OBS_GROUP:
        u, p = stats.mannwhitneyu(top4, rest, alternative="greater")
        results["mannwhitney_top4_vs_resto"] = {
            "test": "Mann-Whitney U",
            "h0": "Las temporadas Top 4 no tienen más puntos que el resto",
            "u_statistic": round(float(u), 4),
            "p_value": round(float(p), 6),
            "significant": bool(p < ALPHA),
            "top4_median": round(float(top4.median()), 2),
            "resto_median": round(float(rest.median()), 2),
        }

    pearson_eff = _pearson(
        kpis["pts_por_gol"],
        kpis["pos_utd"],
        "No hay correlación entre eficiencia (pts/gol) y posición final",
    )
    if pearson_eff:
        results["pearson_eficiencia_vs_posicion"] = pearson_eff

    for name, block in results.items():
        logger.info("[STATS] %s: p=%.4f", name, block["p_value"])
    return results


def managerial_changes(kpis: pd.DataFrame) -> list[dict]:
    """Lista los cambios de entrenador entre temporadas consecutivas."""
    ordered = kpis.sort_values("año").reset_index(drop=True)
    previous = ordered["entrenador"].shift(1)
    mask = previous.notna() & (ordered["entrenador"] != previous)
    return [
        {
            "season": int(ordered.at[i, "año"]),
            "from_manager": str(previous.at[i]),
            "to_manager": str(ordered.at[i, "entrenador"]),
            "index": int(i),
        }
        for i in ordered.index[mask]
    ]


def _window_delta(points: pd.Series, idx: int, window: int) -> tuple[pd.Series, pd.Series]:
    pre = points.iloc[max(0, idx - window) : idx].dropna()
    post = points.iloc[idx : min(len(points), idx + window)].dropna()
    return pre, post


def before_after_analysis(
    kpis: pd.DataFrame,
    window: int = PRE_POST_WINDOW,
    seed: int = PLACEBO_SEED,
    n_simulations: int = PLACEBO_SIMULATIONS,
) -> dict:
    """Comparación descriptiva pre/post de cada cambio de entrenador.

    Para cada cambio compara la media de puntos de las ``window`` temporadas
    previas y posteriores, y contrasta el Δ observado contra ``n_simulations``
    cortes aleatorios (test placebo con semilla fija, reproducible).

    Returns
    -------
    dict
        ``managerial_changes``, ``before_after_estimates``,
        ``before_after_summary``, ``trend_projection`` y ``placebo_test``.
    """
    validate_season_kpis(kpis)
    ordered = kpis.sort_values("año").reset_index(drop=True)
    points = ordered["pts_utd"].astype("float64")
    changes = managerial_changes(ordered)
    results: dict = {"managerial_changes": changes}

    estimates: list[dict] = []
    for change in changes:
        pre, post = _window_delta(points, change["index"], window)
        if pre.empty or post.empty:
            continue
        delta = float(post.mean() - pre.mean())
        if len(pre) >= window and len(post) >= window:
            t_stat, p_value = stats.ttest_ind(pre, post)
        else:
            t_stat, p_value = 0.0, 1.0
        estimates.append(
            {
                "change_season": change["season"],
                "from": change["from_manager"],
                "to": change["to_manager"],
                "pre_points_mean": round(float(pre.mean()), 2),
                "post_points_mean": round(float(post.mean()), 2),
                "delta_points": round(delta, 2),
                "t_statistic": round(float(t_stat), 4),
                "p_value": round(float(p_value), 4),
                "significant": bool(p_value < ALPHA),
                "direction": "mejora" if delta > 0 else "deterioro",
            }
        )
    results["before_after_estimates"] = estimates

    if estimates:
        deltas = np.array([e["delta_points"] for e in estimates])
        results["before_after_summary"] = {
            "n_changes": len(estimates),
            "n_significant": sum(e["significant"] for e in estimates),
            "mean_delta": round(float(deltas.mean()), 2),
            "median_delta": round(float(np.median(deltas)), 2),
            "best_change": max(estimates, key=lambda e: e["delta_points"]),
            "worst_change": min(estimates, key=lambda e: e["delta_points"]),
            "note": "Descriptivo before/after sin grupo control, no es un efecto causal",
        }

    if len(ordered) >= 5:
        slope, intercept = np.polyfit(np.arange(len(points)), points.fillna(points.mean()), 1)
        results["trend_projection"] = {
            "trend_slope": round(float(slope), 3),
            "projected_next_season_points": round(float(slope * len(points) + intercept), 1),
            "last_season_points": round(float(points.iloc[-1]), 1),
            "interpretation": (
                "Tendencia de deterioro"
                if slope < -0.5
                else "Tendencia de mejora"
                if slope > 0.5
                else "Tendencia estable"
            ),
        }

    if estimates and len(points) > 2:
        rng = np.random.default_rng(seed)
        placebo: list[float] = []
        for _ in range(n_simulations):
            cut = int(rng.integers(1, len(points) - 1))
            pre, post = _window_delta(points, cut, window)
            if not pre.empty and not post.empty:
                placebo.append(float(post.mean() - pre.mean()))
        placebo_abs = np.abs(np.array(placebo))
        per_change = []
        for est in estimates:
            p_val = float(np.mean(placebo_abs >= abs(est["delta_points"])))
            per_change.append(
                {
                    "change": f"{est['from']} → {est['to']}",
                    "season": est["change_season"],
                    "delta_points": est["delta_points"],
                    "p_value_placebo": round(p_val, 4),
                    "significant": bool(p_val < ALPHA),
                }
            )
        n_sig = sum(c["significant"] for c in per_change)
        results["placebo_test"] = {
            "seed": seed,
            "n_simulations": n_simulations,
            "n_changes_tested": len(per_change),
            "n_significant": n_sig,
            "per_change": per_change,
            "interpretation": (
                f"Δ pre/post de cada cambio comparado contra {n_simulations} cortes "
                f"aleatorios (semilla {seed}), descriptivo, no causal"
            ),
        }
        logger.info(
            "[PRE/POST] %d cambios; %d significativos según placebo", len(per_change), n_sig
        )
    return results
