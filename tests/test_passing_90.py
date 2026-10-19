"""Tests para src/passing_90.py — pases por 90' con mínimo de 900 minutos."""

import pandas as pd

from src.passing_90 import MIN_90S, compute_passing_90, export_passing_90, render_passing_table


def test_compute_passing_90_filtro_minutos():
    tabla = compute_passing_90()
    assert (tabla["min_90s"] >= MIN_90S).all()
    # Excluidos: jugadores con <900 minutos (p. ej. McTominay 0.6 x 90s)
    assert "Scott McTominay" not in tabla["jugador"].tolist()
    # Excluida: fila de cabecera repetida de la exportación FBref
    assert "Player" not in tabla["jugador"].tolist()


def test_compute_passing_90_valores_conocidos():
    tabla = compute_passing_90()
    bruno = tabla[tabla["jugador"] == "Bruno Fernandes"].iloc[0]
    assert abs(bruno["prgp_90"] - round(463 / 54.7, 2)) < 0.01
    assert abs(bruno["kp_90"] - round(135 / 54.7, 2)) < 0.01
    assert bruno["pct_prgp_plantel"] == 100
    assert bruno["pct_kp_plantel"] == 100


def test_compute_passing_90_columna_prgp_no_prog():
    # La columna FBref se llama PrgP; el DataFrame de salida la refleja calculada
    tabla = compute_passing_90()
    assert {"prgp_90", "kp_90", "pct_prgp_plantel", "pct_kp_plantel"}.issubset(tabla.columns)


def test_export_passing_90_csv(tmp_path):
    tabla = export_passing_90(tmp_path)
    ruta = tmp_path / "data" / "export" / "passing_90_united_2425.csv"
    assert ruta.exists()
    leido = pd.read_csv(ruta)
    assert len(leido) == len(tabla)


def test_render_passing_table():
    tabla = compute_passing_90()
    md = render_passing_table(tabla)
    assert md.startswith("| Jugador |")
    assert "Bruno Fernandes" in md
