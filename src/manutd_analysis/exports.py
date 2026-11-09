"""Exportaciones para herramientas externas (Datawrapper, Flourish, Observable).

Todas las funciones reciben DataFrames ya calculados y un directorio de
salida; no recalculan métricas.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from manutd_analysis.config import TEAM_NAME

logger = logging.getLogger(__name__)


def _json_default(obj: Any) -> Any:
    """Convierte escalares numpy/pandas a tipos nativos para ``json.dump``."""
    if isinstance(obj, np.generic):
        return obj.item()
    if obj is pd.NA or (isinstance(obj, float) and np.isnan(obj)):
        return None
    raise TypeError(f"Objeto de tipo {type(obj).__name__} no serializable a JSON")


def _nan_to_none(obj: Any) -> Any:
    """Reemplaza recursivamente ``NaN`` por ``None`` (``NaN`` no es JSON válido)."""
    if isinstance(obj, dict):
        return {k: _nan_to_none(v) for k, v in obj.items()}
    if isinstance(obj, list | tuple):
        return [_nan_to_none(v) for v in obj]
    if isinstance(obj, float | np.floating) and np.isnan(obj):
        return None
    return obj


def write_json(data: dict, path: Path) -> Path:
    """Escribe ``data`` como JSON UTF-8 estricto (sin ``NaN``), creando el directorio si falta."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("w", encoding="utf-8") as fh:
            json.dump(
                _nan_to_none(data),
                fh,
                ensure_ascii=False,
                indent=2,
                allow_nan=False,
                default=_json_default,
            )
    except (OSError, TypeError):
        logger.exception("No se pudo escribir %s", path)
        raise
    logger.info("JSON escrito: %s", path)
    return path


def write_csv(df: pd.DataFrame, path: Path) -> Path:
    """Escribe ``df`` como CSV UTF-8 sin índice, creando el directorio si falta."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        df.to_csv(path, index=False, encoding="utf-8")
    except OSError:
        logger.exception("No se pudo escribir %s", path)
        raise
    logger.info("CSV escrito: %s (%d filas)", path, len(df))
    return path


def bump_chart_data(kpis: pd.DataFrame) -> pd.DataFrame:
    """Posición y PPG por temporada y entrenador (Flourish bump chart)."""
    return (
        kpis[["año", "pos_utd", "entrenador", "ppg"]]
        .rename(
            columns={"año": "Season", "pos_utd": "Position", "entrenador": "Manager", "ppg": "PPG"}
        )
        .sort_values("Season")
        .reset_index(drop=True)
    )


def correlation_data(kpis: pd.DataFrame, pl_tables: pd.DataFrame) -> pd.DataFrame:
    """Puntos, goles, diferencia, victorias y posición por temporada (Observable).

    Las victorias se toman de la columna ``won`` de las tablas de la liga
    (antes se estimaban con una fórmula incorrecta a partir de puntos y goles).
    """
    corr = kpis[["año", "pts_utd", "gf_utd", "ga_utd", "pos_utd", "entrenador"]].copy()
    corr["gd"] = corr["gf_utd"] - corr["ga_utd"]
    if "won" in pl_tables.columns:
        wins = pl_tables.loc[pl_tables["team"] == TEAM_NAME, ["season_end_year", "won"]]
        corr = corr.merge(wins, left_on="año", right_on="season_end_year", how="left").drop(
            columns="season_end_year"
        )
    return corr.rename(
        columns={
            "año": "Season",
            "pts_utd": "Points",
            "gf_utd": "Goals_For",
            "ga_utd": "Goals_Against",
            "pos_utd": "Position",
            "entrenador": "Manager",
            "gd": "Goal_Difference",
            "won": "Wins",
        }
    )


_EMBED_TEMPLATE = """# Embed snippets, visualizaciones Man Utd

Reemplaza los identificadores `*_ID` por los de tu visualización publicada.

## 1. Datawrapper: benchmark PL (PPG United vs Top 6 vs resto)

```html
<iframe src="https://datawrapper.dwcdn.net/DATASET_ID/" title="Benchmark PL"
  width="100%" height="400" frameborder="0" loading="lazy"></iframe>
```

Datos: `data/export/dw_benchmark_pl.csv`

## 2. Flourish: bump chart por entrenador

```html
<iframe src="https://flo.uri.sh/visualisation/VISUALISATION_ID/embed" title="Bump chart"
  width="100%" height="500" frameborder="0" loading="lazy"></iframe>
```

Datos: `data/export/flourish_bump_manager.csv`

## 3. Observable Plot: matriz de correlación

Datos: `data/export/observable_correlacion.csv`

*Generado por `manutd_analysis.exports`.*
"""


def export_external(
    kpis: pd.DataFrame,
    pl_tables: pd.DataFrame,
    group_bench: pd.DataFrame,
    export_dir: Path,
) -> list[Path]:
    """Escribe los CSV para Datawrapper, Flourish y Observable y los snippets de embed."""
    paths = [
        write_csv(group_bench, export_dir / "dw_benchmark_pl.csv"),
        write_csv(bump_chart_data(kpis), export_dir / "flourish_bump_manager.csv"),
        write_csv(correlation_data(kpis, pl_tables), export_dir / "observable_correlacion.csv"),
    ]
    snippets = export_dir / "embed_snippets.md"
    snippets.write_text(_EMBED_TEMPLATE, encoding="utf-8")
    paths.append(snippets)
    return paths
