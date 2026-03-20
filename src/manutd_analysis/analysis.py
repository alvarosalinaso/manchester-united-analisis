"""Módulo de análisis de rendimiento del Manchester United."""
import pandas as pd


def analizar_eficiencia(df: pd.DataFrame) -> pd.Series:
    """
    Calcula la eficiencia media de puntos por gol por entrenador.

    Args:
        df: DataFrame maestro con columnas 'entrenador' y 'pts_por_gol'.

    Returns:
        Serie ordenada de mayor a menor eficiencia.
    """
    _validar_columnas(df, {"entrenador", "pts_por_gol"})
    return df.groupby("entrenador")["pts_por_gol"].mean().sort_values(ascending=False).round(3)


def analizar_estabilidad(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compara el rendimiento en temporadas estables vs. de transición de técnico.

    Una temporada es de 'transición' si el campo entrenador contiene '/'.

    Args:
        df: DataFrame maestro con columna 'entrenador'.

    Returns:
        DataFrame con métricas promedio para cada categoría.
    """
    _validar_columnas(df, {"entrenador", "pts_utd", "brecha_puntos", "gf_utd"})
    tmp = df.copy()
    tmp["es_transicion"] = tmp["entrenador"].astype(str).str.contains("/", regex=False)
    comparativa = (
        tmp.groupby("es_transicion")[["pts_utd", "brecha_puntos", "gf_utd", "ppg"]]
        .mean()
        .round(2)
    )
    comparativa.index = ["Estable (1 Técnico)", "Transición (Relevo)"]
    return comparativa


def calcular_costo_inestabilidad(comparativa: pd.DataFrame) -> float:
    """
    Calcula los puntos que se pierden en temporadas de transición.

    Args:
        comparativa: Resultado de `analizar_estabilidad`.

    Returns:
        Diferencia de puntos (positiva = el equipo rinde mejor con estabilidad).
    """
    try:
        return float(
            comparativa.loc["Estable (1 Técnico)", "pts_utd"]
            - comparativa.loc["Transición (Relevo)", "pts_utd"]
        )
    except KeyError:
        return 0.0


def resumen_por_entrenador(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera una tabla resumen con todas las métricas por entrenador.

    Args:
        df: DataFrame maestro.

    Returns:
        DataFrame con promedios de pts_utd, gf_utd, ppg, pts_por_gol y brecha_puntos.
    """
    _validar_columnas(df, {"entrenador", "pts_utd", "gf_utd", "ppg", "pts_por_gol", "brecha_puntos"})
    return (
        df.groupby("entrenador")
        .agg(
            temporadas=("año", "count"),
            pts_promedio=("pts_utd", "mean"),
            goles_promedio=("gf_utd", "mean"),
            ppg=("ppg", "mean"),
            eficiencia=("pts_por_gol", "mean"),
            brecha_vs_campeon=("brecha_puntos", "mean"),
        )
        .round(2)
        .sort_values("pts_promedio", ascending=False)
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _validar_columnas(df: pd.DataFrame, requeridas: set) -> None:
    faltantes = requeridas - set(df.columns)
    if faltantes:
        raise ValueError(f"Columnas faltantes en el DataFrame: {faltantes}")
