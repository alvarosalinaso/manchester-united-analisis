"""Ingesta de datos: lectura, saneamiento de cabeceras y casteo estricto de tipos.

Este módulo es la única puerta de entrada de archivos al sistema. Todo lo que
sale de aquí ya está validado (ver :mod:`manutd_analysis.validator`) y tiene
tipos numéricos garantizados, de modo que :mod:`manutd_analysis.metrics` puede
trabajar con funciones puras sin volver a defenderse de datos sucios.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from manutd_analysis.config import ProjectPaths
from manutd_analysis.validator import (
    PASSING_SCHEMA,
    PL_TABLES_SCHEMA,
    SchemaError,
    require_columns,
    require_no_nulls,
    validate_passing,
    validate_pl_tables,
)

logger = logging.getLogger(__name__)

_PL_INT_COLUMNS: tuple[str, ...] = ("season_end_year", "position", "played", "gf", "ga", "points")
_PL_OPTIONAL_INT: tuple[str, ...] = ("won", "drawn", "lost", "gd")
_PASSING_NUMERIC: tuple[str, ...] = ("90s", "KP", "PrgP")


class DataLoadError(RuntimeError):
    """No fue posible leer o interpretar un archivo de entrada."""


def sanitize_headers(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza los nombres de columna sin alterar su capitalización.

    Elimina BOM, comillas y espacios sobrantes, que suelen colarse en
    exportaciones de Excel o de FBref.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame recién leído.

    Returns
    -------
    pd.DataFrame
        Copia con cabeceras limpias.
    """
    cleaned = df.copy()
    cleaned.columns = [
        str(col).replace("﻿", "").strip().strip('"').strip("'").strip() for col in cleaned.columns
    ]
    return cleaned


def _read_csv(path: Path) -> pd.DataFrame:
    """Lee un CSV con manejo explícito de cada modo de falla."""
    if not path.is_file():
        raise DataLoadError(f"No existe el archivo de entrada: {path}")
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError as exc:
        logger.exception("Codificación inválida en %s (se esperaba UTF-8)", path)
        raise DataLoadError(f"Codificación inválida en {path}") from exc
    except pd.errors.EmptyDataError as exc:
        logger.exception("Archivo vacío: %s", path)
        raise DataLoadError(f"Archivo vacío: {path}") from exc
    except pd.errors.ParserError as exc:
        logger.exception("CSV mal formado: %s", path)
        raise DataLoadError(f"CSV mal formado: {path}") from exc
    logger.info("Leído %s (%d filas, %d columnas)", path.name, len(df), df.shape[1])
    return sanitize_headers(df)


def cast_numeric(df: pd.DataFrame, columns: tuple[str, ...]) -> pd.DataFrame:
    """Convierte ``columns`` a numérico; los valores inválidos quedan como ``NaN``.

    Los nulos resultantes se detectan después en la validación, en lugar de
    propagarse en silencio.
    """
    out = df.copy()
    for col in columns:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def load_pl_tables(path: Path | None = None) -> pd.DataFrame:
    """Carga las tablas finales de la Premier League (1993-2024).

    Parameters
    ----------
    path : Path | None
        Ruta del CSV. Por defecto ``data/pl-tables-1993-2024.csv``.

    Returns
    -------
    pd.DataFrame
        Una fila por equipo y temporada, con columnas enteras tipadas
        (``Int64``) y ``team`` como texto sin espacios sobrantes.

    Raises
    ------
    DataLoadError
        Si el archivo no existe o no puede parsearse.
    SchemaError
        Si faltan columnas, hay valores no numéricos o falta cobertura del período.
    """
    path = path or ProjectPaths.default().pl_tables_csv
    df = _read_csv(path)
    require_columns(df, PL_TABLES_SCHEMA, f"Tablas PL ({path.name})")
    df = cast_numeric(df, _PL_INT_COLUMNS)
    require_no_nulls(df, _PL_INT_COLUMNS, f"Tablas PL ({path.name})")
    df = df.astype({col: "int64" for col in _PL_INT_COLUMNS})
    optional = [col for col in _PL_OPTIONAL_INT if col in df.columns]
    df = cast_numeric(df, tuple(optional)).astype({col: "Int64" for col in optional})
    df["team"] = df["team"].astype("string").str.strip()
    return validate_pl_tables(df)


def load_passing(path: Path | None = None) -> pd.DataFrame:
    """Carga la exportación de pases de FBref (plantel United 2024-25).

    FBref repite la fila de cabecera dentro de la tabla y duplica nombres de
    columna (``Cmp``, ``Att``...). Esta función descarta esas filas espurias y
    castea a numérico las columnas usadas por las métricas.

    Raises
    ------
    DataLoadError
        Si el archivo no existe o no puede parsearse.
    SchemaError
        Si faltan columnas obligatorias o no queda ningún jugador válido.
    """
    path = path or ProjectPaths.default().passing_csv
    df = _read_csv(path)
    require_columns(df, PASSING_SCHEMA, f"Pases FBref ({path.name})")
    raw_rows = len(df)
    df = df[df["Player"].notna() & (df["Player"] != "Player")].copy()
    df = cast_numeric(df, _PASSING_NUMERIC)
    invalid = df[list(_PASSING_NUMERIC)].isna().any(axis=1)
    if invalid.any():
        logger.warning(
            "Pases FBref: %d filas con métricas no numéricas descartadas", int(invalid.sum())
        )
    df = df[~invalid].reset_index(drop=True)
    logger.info("Pases FBref: %d jugadores válidos de %d filas", len(df), raw_rows)
    if df.empty:
        raise SchemaError("Pases FBref: no quedan jugadores válidos tras el saneamiento")
    return validate_passing(df)
