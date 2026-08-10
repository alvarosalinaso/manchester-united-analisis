"""Tests para el módulo de visualización (matplotlib, backend Agg)."""

import matplotlib

matplotlib.use("Agg")

import pandas as pd
import pytest

from manutd_analysis.plots import (
    graficar_eficiencia_y_brecha,
    graficar_ppg_historico,
    graficar_rentabilidad_ofensiva,
)


@pytest.fixture
def df_manutd() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "año": [2015, 2016, 2019, 2020],
            "entrenador": ["Van Gaal", "Van Gaal", "Mourinho / Solskjær", "Solskjær"],
            "gf_utd": [62, 49, 65, 66],
            "brecha_puntos": [17, 27, 40, 20],
            "ppg": [1.842, 1.737, 1.526, 1.737],
            "pts_por_gol": [1.13, 1.35, 0.89, 1.00],
        }
    )


def test_graficar_eficiencia_y_brecha(df_manutd, tmp_path):
    ruta = graficar_eficiencia_y_brecha(df_manutd, out_dir=str(tmp_path))
    assert ruta.name == "eficiencia_y_brecha.png"
    assert ruta.exists()
    assert ruta.stat().st_size > 0


def test_graficar_rentabilidad_ofensiva(df_manutd, tmp_path):
    ruta = graficar_rentabilidad_ofensiva(df_manutd, out_dir=str(tmp_path))
    assert ruta.name == "rentabilidad_ofensiva.png"
    assert ruta.exists()


def test_graficar_ppg_historico(df_manutd, tmp_path):
    ruta = graficar_ppg_historico(df_manutd, out_dir=str(tmp_path))
    assert ruta.name == "ppg_historico.png"
    assert ruta.exists()
