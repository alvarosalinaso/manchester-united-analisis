"""Test suite para manutd_analysis."""
import pytest
import pandas as pd
from manutd_analysis.data import cargar_y_filtrar_datos, ENTRENADORES
from manutd_analysis.analysis import analizar_eficiencia, analizar_estabilidad, calcular_costo_inestabilidad

# Fixture con datos falsos
@pytest.fixture
def mock_df():
    data = {
        'entrenador': ['Mourinho', 'Mourinho', 'Solskjær/Rangnick', 'Moyes'],
        'pts_por_gol': [1.5, 1.4, 1.0, 1.2],
        'pts_utd': [81, 66, 58, 64],
        'brecha_puntos': [19, 32, 35, 22],
        'gf_utd': [68, 54, 57, 64],
        'entrenador': ['A', 'A', 'A/B', 'C']
    }
    return pd.DataFrame(data)

def test_data_loading_smoke():
    """Smoke test: Verifica que cargar_y_filtrar_datos no explote con archivo inexistente."""
    # Debería retornar None o manejar gracefully el error
    result = cargar_y_filtrar_datos('archivo_que_no_existe.csv')
    assert result is None

def test_analizar_eficiencia(mock_df):
    """Verifica el cálculo de eficiencia por entrenador."""
    res = analizar_eficiencia(mock_df)
    # Entrenador A: (1.5 + 1.4) / 2 = 1.45
    # Entrenador C: 1.2
    # Entrenador A/B: 1.0
    assert 'A' in res.index
    assert res['A'] == pytest.approx(1.45)

def test_analizar_estabilidad(mock_df):
    """Verifica clasificación de estabilidad/transición."""
    res = analizar_estabilidad(mock_df)
    assert 'Estable (1 Técnico)' in res.index
    assert 'Transición (Relevo)' in res.index
    
    # A y C son estables. A/B es transición.
    # Pts estables: (81+66+64)/3 = 70.3
    # Pts transición: 58
    # Comprobamos que existan las filas
    assert not res.empty

def test_calcular_costo_inestabilidad():
    """Verifica cálculo simple de costo."""
    df_comp = pd.DataFrame({
        'pts_utd': [80, 60]
    }, index=['Estable (1 Técnico)', 'Transición (Relevo)'])
    
    costo = calcular_costo_inestabilidad(df_comp)
    assert costo == 20
