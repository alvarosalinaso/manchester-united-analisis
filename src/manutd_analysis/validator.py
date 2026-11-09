"""Validación temprana (fail-fast) de esquemas de datos.

Cada función lanza :class:`SchemaError` en cuanto detecta un problema, con un
mensaje que nombra la fuente y las columnas afectadas. Así un CSV corrupto o
con columnas renombradas se detiene en la ingesta y no produce métricas
silenciosamente vacías más adelante.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable

import pandas as pd

from manutd_analysis.config import SEASONS, TEAM_NAME

logger = logging.getLogger(__name__)

#: Columnas obligatorias de las tablas finales de la Premier League.
PL_TABLES_SCHEMA: frozenset[str] = frozenset(
    {"season_end_year", "team", "position", "played", "gf", "ga", "points"}
)

#: Columnas obligatorias de la exportación de pases de FBref.
PASSING_SCHEMA: frozenset[str] = frozenset({"Player", "Pos", "90s", "KP", "PrgP"})

#: Columnas obligatorias del DataFrame de KPIs por temporada del United.
SEASON_KPIS_SCHEMA: frozenset[str] = frozenset(
    {
        "año",
        "pts_utd",
        "pos_utd",
        "gf_utd",
        "ga_utd",
        "played",
        "entrenador",
        "pts_champ",
        "gf_champ",
        "ga_champ",
        "brecha_puntos",
        "brecha_ataque",
        "brecha_defensa",
        "pts_por_gol",
        "ppg",
        "es_transicion",
    }
)


class SchemaError(ValueError):
    """El DataFrame no cumple el contrato de datos esperado."""


def require_columns(df: pd.DataFrame, required: Iterable[str], source: str = "DataFrame") -> None:
    """Verifica que ``df`` contenga todas las columnas de ``required``.

    Parameters
    ----------
    df : pd.DataFrame
        Datos a validar.
    required : Iterable[str]
        Columnas obligatorias.
    source : str
        Nombre legible de la fuente, usado en el mensaje de error.

    Raises
    ------
    SchemaError
        Si falta al menos una columna.
    """
    missing = set(required) - set(df.columns)
    if missing:
        raise SchemaError(f"{source}: faltan columnas obligatorias {sorted(missing)}")


def require_not_empty(df: pd.DataFrame, source: str = "DataFrame") -> None:
    """Falla si ``df`` no tiene filas."""
    if df.empty:
        raise SchemaError(f"{source}: no contiene filas")


def require_no_nulls(df: pd.DataFrame, columns: Iterable[str], source: str = "DataFrame") -> None:
    """Falla si alguna de ``columns`` contiene nulos (p. ej. tras un casteo fallido)."""
    cols = list(columns)
    nulls = df[cols].isna().sum()
    bad = nulls[nulls > 0]
    if not bad.empty:
        raise SchemaError(f"{source}: valores nulos o no numéricos en {bad.to_dict()}")


def validate_pl_tables(df: pd.DataFrame) -> pd.DataFrame:
    """Valida las tablas de la Premier League y la cobertura del período.

    Comprueba columnas obligatorias, ausencia de nulos en las columnas
    numéricas, que el United aparezca en todas las temporadas analizadas y que
    exista un único campeón por temporada.

    Returns
    -------
    pd.DataFrame
        El mismo DataFrame, para encadenar llamadas.
    """
    source = "Tablas PL"
    require_columns(df, PL_TABLES_SCHEMA, source)
    require_not_empty(df, source)
    require_no_nulls(df, PL_TABLES_SCHEMA, source)

    period = df[df["season_end_year"].isin(SEASONS)]
    united_seasons = set(period.loc[period["team"] == TEAM_NAME, "season_end_year"])
    missing_seasons = sorted(set(SEASONS) - united_seasons)
    if missing_seasons:
        raise SchemaError(f"{source}: '{TEAM_NAME}' no aparece en las temporadas {missing_seasons}")

    champions = period[period["position"] == 1].groupby("season_end_year").size()
    duplicated = champions[champions != 1]
    if not duplicated.empty:
        raise SchemaError(f"{source}: más de un campeón en {duplicated.index.tolist()}")

    if (df["played"] <= 0).any():
        raise SchemaError(f"{source}: hay filas con 'played' <= 0")

    logger.debug("%s válidas: %d filas", source, len(df))
    return df


def validate_passing(df: pd.DataFrame) -> pd.DataFrame:
    """Valida la exportación de pases de FBref (columnas y filas con jugador)."""
    source = "Pases FBref"
    require_columns(df, PASSING_SCHEMA, source)
    require_not_empty(df, source)
    return df


def validate_season_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Valida el DataFrame de KPIs por temporada antes de los análisis aguas abajo."""
    source = "KPIs por temporada"
    require_columns(df, SEASON_KPIS_SCHEMA, source)
    require_not_empty(df, source)
    if df["año"].duplicated().any():
        raise SchemaError(f"{source}: temporadas duplicadas")
    return df
