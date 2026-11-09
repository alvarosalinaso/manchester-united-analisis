"""Tests de métricas puras."""

import math

import numpy as np
import pandas as pd
import pytest

from manutd_analysis import metrics
from manutd_analysis.config import SEASONS, TEAM_NAME
from manutd_analysis.metrics import STABLE_LABEL, TRANSITION_LABEL


def test_safe_divide_cero_es_nan():
    out = metrics.safe_divide(pd.Series([10, 5]), pd.Series([2, 0]))
    assert out.iloc[0] == 5.0
    assert np.isnan(out.iloc[1])


def test_safe_divide_fill_value():
    assert metrics.safe_divide(pd.Series([1]), pd.Series([0]), fill_value=0.0).iloc[0] == 0.0


def test_build_season_kpis_estructura(kpis):
    assert kpis["año"].tolist() == list(SEASONS)
    first = kpis.iloc[0]
    assert first["brecha_puntos"] == 90 - 70
    assert first["ppg"] == pytest.approx(70 / 38, abs=1e-3)
    assert kpis["es_transicion"].sum() == 2  # 2019 y 2022


def test_build_season_kpis_goles_cero_no_rompe(synthetic_pl):
    df = synthetic_pl.copy()
    df.loc[(df["team"] == TEAM_NAME) & (df["season_end_year"] == 2014), "gf"] = 0
    kpis = metrics.build_season_kpis(df)
    assert np.isnan(kpis.loc[kpis["año"] == 2014, "pts_por_gol"].iloc[0])


def test_efficiency_by_manager_orden(kpis):
    assert metrics.efficiency_by_manager(kpis).is_monotonic_decreasing


def test_ppg_by_manager_excluye_transiciones(kpis):
    assert not any("/" in name for name in metrics.ppg_by_manager(kpis).index)
    with_transitions = metrics.ppg_by_manager(kpis, exclude_transitions=False)
    assert any("/" in name for name in with_transitions.index)


def test_stability_y_costo():
    df = pd.DataFrame(
        {
            "entrenador": ["A", "B", "A / B", "C"],
            "pts_utd": [70, 70, 60, 70],
            "brecha_puntos": [10, 10, 20, 10],
            "gf_utd": [60, 60, 50, 60],
            "ppg": [1.8, 1.8, 1.6, 1.8],
        }
    )
    comp = metrics.stability_comparison(df)
    assert list(comp.index) == [STABLE_LABEL, TRANSITION_LABEL]
    assert metrics.instability_cost(comp) == 10.0


def test_stability_sin_transiciones_no_falla():
    df = pd.DataFrame(
        {
            "entrenador": ["A", "B"],
            "pts_utd": [70, 60],
            "brecha_puntos": [1, 2],
            "gf_utd": [1, 2],
            "ppg": [1.0, 1.0],
        }
    )
    comp = metrics.stability_comparison(df)
    assert list(comp.index) == [STABLE_LABEL]
    assert math.isnan(metrics.instability_cost(comp))


def test_manager_summary(kpis):
    summary = metrics.manager_summary(kpis)
    assert summary["pts_promedio"].is_monotonic_decreasing
    assert summary["temporadas"].sum() == len(kpis)


def test_league_benchmark(synthetic_pl):
    bench = metrics.league_benchmark(synthetic_pl)
    assert bench["temporada"].tolist() == list(SEASONS)
    row = bench.iloc[0]
    assert row["pl_avg_pts_sin_utd"] == pytest.approx((90 + 45) / 2, abs=0.1)
    expected = row["united_ppg"] - row["pl_avg_ppg_sin_utd"]
    assert row["diff_ppg_vs_pl"] == pytest.approx(expected, abs=1e-3)


def test_group_benchmark(synthetic_pl):
    groups = metrics.group_benchmark(synthetic_pl)
    assert set(groups["Grupo"]) == {TEAM_NAME, "Resto PL"}


def test_passing_per_90_filtro_y_percentiles():
    df = pd.DataFrame(
        {
            "Player": ["A", "B", "C"],
            "Pos": ["MF"] * 3,
            "90s": [20.0, 10.0, 5.0],
            "KP": [40.0, 10.0, 50.0],
            "PrgP": [100.0, 80.0, 99.0],
        }
    )
    out = metrics.passing_per_90(df, min_minutes=900)
    assert out["jugador"].tolist() == ["B", "A"]  # C excluido (<900 min)
    assert out.loc[out["jugador"] == "B", "pct_prgp_plantel"].iloc[0] == 100


def test_key_findings_datos_reales(repo_paths):
    from manutd_analysis.data_loader import load_pl_tables

    pl = load_pl_tables(repo_paths.pl_tables_csv)
    findings = metrics.key_findings(metrics.build_season_kpis(pl), metrics.league_benchmark(pl))
    assert findings["n_temporadas"] == 11
    assert findings["brecha_media"] == 23.1
    assert findings["mejor_dt"] == {"nombre": "José Mourinho", "ppg": 1.97}
    assert findings["peor_dt"] == {"nombre": "David Moyes", "ppg": 1.68}
    assert findings["costo_inestabilidad"] == 7.4
    assert findings["ventaja_ppg_vs_pl"] > 0
