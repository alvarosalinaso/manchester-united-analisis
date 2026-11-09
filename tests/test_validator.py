"""Tests de validación fail-fast."""

import pandas as pd
import pytest

from manutd_analysis.config import TEAM_NAME
from manutd_analysis.validator import (
    SchemaError,
    require_columns,
    require_no_nulls,
    validate_pl_tables,
    validate_season_kpis,
)


def test_require_columns_ok():
    require_columns(pd.DataFrame({"a": [1], "b": [2]}), {"a"})


def test_require_columns_falla_con_lista_de_faltantes():
    with pytest.raises(SchemaError, match=r"\['b', 'c'\]"):
        require_columns(pd.DataFrame({"a": [1]}), {"a", "b", "c"}, "fuente")


def test_require_no_nulls_detecta_casteo_fallido():
    with pytest.raises(SchemaError, match="nulos"):
        require_no_nulls(pd.DataFrame({"x": [1.0, None]}), ["x"])


def test_validate_pl_tables_ok(synthetic_pl):
    assert validate_pl_tables(synthetic_pl) is synthetic_pl


def test_validate_pl_tables_falta_temporada_united(synthetic_pl):
    mask = (synthetic_pl["team"] == TEAM_NAME) & (synthetic_pl["season_end_year"] == 2020)
    with pytest.raises(SchemaError, match="2020"):
        validate_pl_tables(synthetic_pl[~mask])


def test_validate_pl_tables_doble_campeon(synthetic_pl):
    df = synthetic_pl.copy()
    df.loc[df["team"] == "Other FC", "position"] = 1
    with pytest.raises(SchemaError, match="campeón"):
        validate_pl_tables(df)


def test_validate_pl_tables_played_cero(synthetic_pl):
    df = synthetic_pl.copy()
    df.loc[0, "played"] = 0
    with pytest.raises(SchemaError, match="played"):
        validate_pl_tables(df)


def test_validate_season_kpis_duplicados(kpis):
    with pytest.raises(SchemaError, match="duplicadas"):
        validate_season_kpis(pd.concat([kpis, kpis.head(1)]))


def test_validate_season_kpis_vacio(kpis):
    with pytest.raises(SchemaError, match="no contiene filas"):
        validate_season_kpis(kpis.iloc[0:0])
