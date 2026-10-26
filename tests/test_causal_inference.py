"""Tests para src/causal_inference.py, placebo con semilla sobre todos los cambios."""

from src.causal_inference import PLACEBO_SEED, run_causal_analysis


def test_placebo_cubre_todos_los_cambios(tmp_path):
    results = run_causal_analysis(output_dir=tmp_path)
    assert "placebo_test" in results
    placebo = results["placebo_test"]
    assert placebo["seed"] == PLACEBO_SEED
    assert placebo["n_changes_tested"] == len(results["before_after_estimates"])
    assert placebo["n_changes_tested"] >= 2
    for cambio in placebo["per_change"]:
        assert 0.0 <= cambio["p_value_placebo"] <= 1.0
        assert isinstance(cambio["significant"], bool)


def test_placebo_reproducible(tmp_path):
    r1 = run_causal_analysis(output_dir=tmp_path / "a")
    r2 = run_causal_analysis(output_dir=tmp_path / "b")
    assert r1["placebo_test"] == r2["placebo_test"]


def test_json_export_valido(tmp_path):
    import json

    run_causal_analysis(output_dir=tmp_path)
    data = json.loads((tmp_path / "before_after_analysis.json").read_text(encoding="utf-8"))
    assert "placebo_test" in data
    assert data["placebo_test"]["seed"] == PLACEBO_SEED
