"""Tests for analysis module (manchester-united-analisis)."""

import pandas as pd
import pytest

from manutd_analysis.analysis import (
    _validar_columnas,
    analizar_eficiencia,
    analizar_estabilidad,
    calcular_costo_inestabilidad,
    resumen_por_entrenador,
)


def test_analizar_eficiencia():
    """Test analizar_eficiencia returns correct series."""
    df = pd.DataFrame(
        {
            "entrenador": ["Moyes", "Van Gaal", "Mourinho", "Moyes"],
            "pts_por_gol": [1.5, 2.0, 1.8, 1.6],
        }
    )
    result = analizar_eficiencia(df)
    assert isinstance(result, pd.Series)
    assert len(result) == 3  # 3 unique managers
    assert result.iloc[0] == 2.0  # Van Gaal highest
    assert result.index[0] == "Van Gaal"


def test_analizar_eficiencia_invalid_columns():
    """Test analizar_eficiencia raises ValueError on missing columns."""
    df = pd.DataFrame({"entrenador": ["Moyes"]})
    with pytest.raises(ValueError, match="Columnas faltantes"):
        analizar_eficiencia(df)


def test_analizar_estabilidad():
    """Test analizar_estabilidad returns correct comparison."""
    df = pd.DataFrame(
        {
            "entrenador": ["Moyes", "Van Gaal", "Mourinho/Solskjaer", "Solskjaer"],
            "pts_utd": [60, 70, 65, 68],
            "brecha_puntos": [20, 15, 18, 12],
            "gf_utd": [60, 65, 62, 66],
            "ppg": [1.6, 1.8, 1.7, 1.8],
        }
    )
    result = analizar_estabilidad(df)
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (2, 4)
    assert "Estable (1 Técnico)" in result.index
    assert "Transición (Relevo)" in result.index


def test_calcular_costo_inestabilidad():
    """Test calcular_costo_inestabilidad returns correct difference."""
    comp = pd.DataFrame(
        {
            "pts_utd": [70, 60],
            "brecha_puntos": [15, 20],
        },
        index=["Estable (1 Técnico)", "Transición (Relevo)"],
    )
    result = calcular_costo_inestabilidad(comp)
    assert result == 10.0


def test_calcular_costo_inestabilidad_missing_key():
    """Test calcular_costo_inestabilidad handles missing keys gracefully."""
    comp = pd.DataFrame({"pts_utd": [70]})
    result = calcular_costo_inestabilidad(comp)
    assert result == 0.0


def test_resumen_por_entrenador():
    """Test resumen_por_entrenador returns correct summary."""
    df = pd.DataFrame(
        {
            "entrenador": ["Moyes", "Van Gaal", "Mourinho", "Moyes"],
            "año": [2014, 2015, 2016, 2014],
            "pts_utd": [60, 70, 65, 62],
            "gf_utd": [60, 65, 62, 61],
            "ppg": [1.6, 1.8, 1.7, 1.6],
            "pts_por_gol": [1.5, 2.0, 1.8, 1.6],
            "brecha_puntos": [20, 15, 18, 19],
        }
    )
    result = resumen_por_entrenador(df)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3  # 3 unique managers
    assert "temporadas" in result.columns
    assert "pts_promedio" in result.columns
    assert result.index[0] == "Van Gaal"  # Highest pts_promedio


def test_validar_columnas_valid():
    """Test _validar_columnas passes with all required columns."""
    df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})
    _validar_columnas(df, {"a", "b"})  # Should not raise


def test_validar_columnas_invalid():
    """Test _validar_columnas raises ValueError on missing columns."""
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(ValueError, match="Columnas faltantes"):
        _validar_columnas(df, {"a", "b", "c"})
