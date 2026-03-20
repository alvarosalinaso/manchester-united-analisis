"""Test suite para manutd_analysis."""
import pytest
import pandas as pd
from manutd_analysis.data import cargar_y_filtrar_datos, ENTRENADORES
from manutd_analysis.analysis import (
    analizar_eficiencia,
    analizar_estabilidad,
    calcular_costo_inestabilidad,
    resumen_por_entrenador,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_df() -> pd.DataFrame:
    """DataFrame mínimo con 4 temporadas ficticias."""
    return pd.DataFrame({
        "año":           [2015, 2016, 2019, 2020],
        "entrenador":    ["Van Gaal", "Van Gaal", "Mourinho / Solskjær", "Solskjær"],
        "pts_utd":       [70, 66, 58, 66],
        "pos_utd":       [4, 5, 6, 3],
        "gf_utd":        [62, 49, 65, 66],
        "ga_utd":        [37, 35, 54, 36],
        "played":        [38, 38, 38, 38],
        "pts_champ":     [87, 93, 98, 86],
        "gf_champ":      [98, 106, 106, 102],
        "ga_champ":      [22, 27, 35, 35],
        "brecha_puntos": [17, 27, 40, 20],
        "brecha_ataque": [36, 57, 41, 36],
        "brecha_defensa":[15, 8, 19, 1],
        "pts_por_gol":   [1.13, 1.35, 0.89, 1.00],
        "ppg":           [1.842, 1.737, 1.526, 1.737],
    })


# ── Tests: carga de datos ─────────────────────────────────────────────────────

def test_data_loading_archivo_inexistente():
    """Si el archivo no existe, debe retornar None sin lanzar excepción."""
    result = cargar_y_filtrar_datos("archivo_que_no_existe.csv")
    assert result is None


def test_entrenadores_cubre_todas_las_temporadas():
    """El mapa de entrenadores debe cubrir exactamente las temporadas 2014-2024."""
    temporadas_esperadas = set(range(2014, 2025))
    assert set(ENTRENADORES.keys()) == temporadas_esperadas


# ── Tests: análisis ───────────────────────────────────────────────────────────

def test_analizar_eficiencia_retorna_serie(mock_df):
    res = analizar_eficiencia(mock_df)
    assert isinstance(res, pd.Series)


def test_analizar_eficiencia_orden_descendente(mock_df):
    res = analizar_eficiencia(mock_df)
    assert list(res.values) == sorted(res.values, reverse=True)


def test_analizar_eficiencia_valores_correctos(mock_df):
    res = analizar_eficiencia(mock_df)
    # Van Gaal: (1.13 + 1.35) / 2 = 1.24
    assert res["Van Gaal"] == pytest.approx(1.24, abs=0.01)


def test_analizar_eficiencia_columnas_faltantes():
    df_malo = pd.DataFrame({"entrenador": ["A"], "pts_utd": [70]})
    with pytest.raises(ValueError, match="Columnas faltantes"):
        analizar_eficiencia(df_malo)


def test_analizar_estabilidad_indice(mock_df):
    res = analizar_estabilidad(mock_df)
    assert "Estable (1 Técnico)" in res.index
    assert "Transición (Relevo)" in res.index


def test_analizar_estabilidad_pts_estable_mayor(mock_df):
    """Los años estables deben tener más puntos que los de transición."""
    res = analizar_estabilidad(mock_df)
    assert res.loc["Estable (1 Técnico)", "pts_utd"] > res.loc["Transición (Relevo)", "pts_utd"]


def test_calcular_costo_inestabilidad_positivo(mock_df):
    comparativa = analizar_estabilidad(mock_df)
    costo = calcular_costo_inestabilidad(comparativa)
    assert costo > 0


def test_calcular_costo_inestabilidad_key_error():
    """Con un DataFrame vacío/incorrecto debe retornar 0.0."""
    df_vacio = pd.DataFrame(index=["Otra categoría"])
    resultado = calcular_costo_inestabilidad(df_vacio)
    assert resultado == 0.0


def test_resumen_por_entrenador_shape(mock_df):
    res = resumen_por_entrenador(mock_df)
    # 3 entrenadores distintos en el fixture
    assert len(res) == 3
    assert "temporadas" in res.columns
    assert "pts_promedio" in res.columns
