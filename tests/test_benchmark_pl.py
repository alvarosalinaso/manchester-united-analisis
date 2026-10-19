"""Tests para src/benchmark_pl.py — benchmark PL sin United."""

import pandas as pd

from src.benchmark_pl import compute_benchmark, export_benchmark, render_benchmark_table


def test_compute_benchmark_estructura():
    bench = compute_benchmark()
    assert len(bench) == 11
    assert list(bench.columns) == [
        "temporada",
        "united_pts",
        "united_ppg",
        "pl_avg_pts_sin_utd",
        "pl_avg_ppg_sin_utd",
        "diff_ppg_vs_pl",
    ]
    assert bench["temporada"].tolist() == list(range(2014, 2025))


def test_compute_benchmark_valores_conocidos():
    bench = compute_benchmark()
    fila_2014 = bench[bench["temporada"] == 2014].iloc[0]
    assert fila_2014["united_pts"] == 64
    assert abs(fila_2014["united_ppg"] - 64 / 38) < 0.001
    # La media PL excluye al United: 19 equipos en 2014
    assert 1.0 < fila_2014["pl_avg_ppg_sin_utd"] < 2.5
    esperado = fila_2014["united_ppg"] - fila_2014["pl_avg_ppg_sin_utd"]
    assert abs(fila_2014["diff_ppg_vs_pl"] - esperado) < 0.001


def test_export_benchmark_csv(tmp_path):
    bench = export_benchmark(tmp_path)
    ruta = tmp_path / "data" / "export" / "pl_benchmark_por_temporada.csv"
    assert ruta.exists()
    leido = pd.read_csv(ruta)
    assert len(leido) == len(bench)


def test_render_benchmark_table():
    bench = compute_benchmark()
    tabla = render_benchmark_table(bench)
    assert tabla.startswith("| Season |")
    assert "| 2014 |" in tabla
    assert "| 2024 |" in tabla
