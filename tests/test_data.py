"""Tests para el módulo de carga de datos del Manchester United."""

import pandas as pd
import pytest

from manutd_analysis.data import ENTRENADORES, _resolver_ruta, cargar_y_filtrar_datos


@pytest.fixture
def pl_csv(tmp_path) -> str:
    """CSV mínimo de Premier League con una temporada campeona por año."""
    path = tmp_path / "pl-tables.csv"
    pd.DataFrame(
        {
            "team": ["Manchester Utd", "Manchester Utd", "Manchester City", "Chelsea"],
            "season_end_year": [2014, 2015, 2014, 2015],
            "points": [64, 70, 86, 87],
            "position": [7, 4, 1, 1],
            "gf": [64, 62, 102, 98],
            "ga": [43, 37, 32, 30],
            "played": [38, 38, 38, 38],
        }
    ).to_csv(path, index=False)
    return str(path)


def test_cargar_y_filtrar_datos_estructura(pl_csv):
    df = cargar_y_filtrar_datos(pl_csv)
    assert df is not None
    assert len(df) == 2
    assert {"pts_utd", "pos_utd", "gf_utd", "ga_utd", "entrenador", "pts_champ"}.issubset(
        df.columns
    )


def test_cargar_y_filtrar_datos_kpis(pl_csv):
    df = cargar_y_filtrar_datos(pl_csv)
    assert df.loc[0, "brecha_puntos"] == 22  # 86 - 64
    assert df.loc[1, "brecha_puntos"] == 17  # 87 - 70
    assert df.loc[0, "entrenador"] == "David Moyes"
    assert df.loc[1, "entrenador"] == "Louis van Gaal"
    assert df.loc[0, "ppg"] == pytest.approx(64 / 38, abs=0.001)


def test_cargar_y_filtrar_datos_archivo_inexistente(tmp_path):
    assert cargar_y_filtrar_datos(str(tmp_path / "no_existe.csv")) is None


def test_cargar_y_filtrar_datos_columnas_incompletas(tmp_path):
    path = tmp_path / "malo.csv"
    pd.DataFrame({"team": ["X"], "season_end_year": [2014]}).to_csv(path, index=False)
    assert cargar_y_filtrar_datos(str(path)) is None


def test_resolver_ruta_absoluta(tmp_path):
    archivo = tmp_path / "datos.csv"
    archivo.write_text("a\n1\n", encoding="utf-8")
    assert _resolver_ruta(str(archivo)) == archivo.resolve()


def test_resolver_ruta_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        _resolver_ruta(str(tmp_path / "no_existe.csv"))


def test_entrenadores_cubre_temporadas():
    assert set(ENTRENADORES.keys()) == set(range(2014, 2025))
