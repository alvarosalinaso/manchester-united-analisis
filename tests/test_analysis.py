"""Smoke tests for manchester-united-analisis."""


def test_imports():
    from src.causal_inference import run_causal_analysis
    from src.cohort_analysis import run_cohort_analysis
    from src.generate_report import generate_report
    from src.generate_tables import generate
    from src.statistical_tests import run_statistical_tests

    assert callable(run_causal_analysis)
    assert callable(run_cohort_analysis)
    assert callable(run_statistical_tests)
    assert callable(generate)
    assert callable(generate_report)
