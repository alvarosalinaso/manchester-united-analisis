"""Módulo de análisis de rendimiento."""
import pandas as pd

def analizar_eficiencia(df: pd.DataFrame) -> pd.Series:
    """Analiza la eficiencia de puntos por gol por entrenador."""
    if 'entrenador' not in df.columns or 'pts_por_gol' not in df.columns:
        raise ValueError("El DataFrame debe contener 'entrenador' y 'pts_por_gol'")
    
    return df.groupby('entrenador')['pts_por_gol'].mean().sort_values(ascending=False)

def analizar_estabilidad(df: pd.DataFrame) -> pd.DataFrame:
    """Analiza el impacto de los cambios de entrenador."""
    df = df.copy()
    if 'entrenador' not in df.columns:
         raise ValueError("El DataFrame debe contener 'entrenador'")

    df['es_transicion'] = df['entrenador'].astype(str).str.contains('/')
    comparativa = df.groupby('es_transicion')[['pts_utd', 'brecha_puntos', 'gf_utd']].mean().round(1)
    comparativa.index = ['Estable (1 Técnico)', 'Transición (Relevo)']
    return comparativa

def calcular_costo_inestabilidad(comparativa: pd.DataFrame) -> float:
    """Calcula la diferencia de puntos entre años estables y de transición."""
    try:
        pts_estable = comparativa.loc['Estable (1 Técnico)', 'pts_utd']
        pts_transicion = comparativa.loc['Transición (Relevo)', 'pts_utd']
        return pts_estable - pts_transicion
    except KeyError:
        return 0.0
