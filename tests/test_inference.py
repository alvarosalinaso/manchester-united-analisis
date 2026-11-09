"""Tests de inferencia estadística, cohortes y comparación pre/post."""

import math

from manutd_analysis.cohorts import cohort_analysis, manager_cohorts
from manutd_analysis.config import PLACEBO_SEED
from manutd_analysis.inference import (
    before_after_analysis,
    managerial_changes,
    statistical_tests,
)


def test_managerial_changes(kpis):
    changes = managerial_changes(kpis)
    assert changes[0]["season"] == 2015
    assert changes[0]["from_manager"] == "David Moyes"
    assert len(changes) == 6


def test_statistical_tests_bloques(kpis):
    res = statistical_tests(kpis)
    assert "pearson_brecha_puntos_vs_ataque" in res
    for block in res.values():
        assert 0.0 <= block["p_value"] <= 1.0
        assert isinstance(block["significant"], bool)


def test_before_after_placebo_reproducible(kpis):
    a = before_after_analysis(kpis)
    b = before_after_analysis(kpis)
    assert a["placebo_test"] == b["placebo_test"]
    assert a["placebo_test"]["seed"] == PLACEBO_SEED
    assert a["placebo_test"]["n_changes_tested"] == len(a["before_after_estimates"])
    assert "trend_projection" in a


def test_manager_cohorts(kpis):
    cohorts = manager_cohorts(kpis)
    assert cohorts["tenure_seasons"].sum() == len(kpis)
    single = cohorts[cohorts["tenure_seasons"] == 1]
    assert single["stability_score"].map(math.isnan).all()


def test_cohort_analysis_resumen(kpis):
    res = cohort_analysis(kpis)
    assert res["tenure_summary"]["n_managers"] == 7
    assert res["tenure_summary"]["turnover_rate"] == round(7 / 11 * 10, 2)
    assert res["transition_analysis"]["total_transitions"] == 6
