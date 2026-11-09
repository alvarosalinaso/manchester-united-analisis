"""Tests de ingesta: saneamiento de cabeceras, casteo y modos de falla."""

import pandas as pd
import pytest

from manutd_analysis.data_loader import (
    DataLoadError,
    load_passing,
    load_pl_tables,
    sanitize_headers,
)
from manutd_analysis.validator import SchemaError


def test_sanitize_headers_quita_bom_comillas_y_espacios():
    df = pd.DataFrame(columns=["﻿team", ' "points" ', "PrgP "])
    assert list(sanitize_headers(df).columns) == ["team", "points", "PrgP"]


def test_load_pl_tables_tipado(synthetic_pl_csv):
    df = load_pl_tables(synthetic_pl_csv)
    assert df["points"].dtype == "int64"
    assert df["season_end_year"].dtype == "int64"
    assert str(df["won"].dtype) == "Int64"


def test_load_pl_tables_valor_no_numerico(tmp_path, synthetic_pl):
    bad = synthetic_pl.astype({"points": "object"})
    bad.loc[0, "points"] = "n/a"
    path = tmp_path / "bad.csv"
    bad.to_csv(path, index=False)
    with pytest.raises(SchemaError, match="points"):
        load_pl_tables(path)


def test_load_pl_tables_columna_faltante(tmp_path, synthetic_pl):
    path = tmp_path / "bad.csv"
    synthetic_pl.drop(columns="gf").to_csv(path, index=False)
    with pytest.raises(SchemaError, match="gf"):
        load_pl_tables(path)


def test_load_archivo_inexistente(tmp_path):
    with pytest.raises(DataLoadError, match="No existe"):
        load_pl_tables(tmp_path / "nada.csv")


def test_load_archivo_vacio(tmp_path):
    path = tmp_path / "vacio.csv"
    path.write_text("", encoding="utf-8")
    with pytest.raises(DataLoadError, match="vacío"):
        load_pl_tables(path)


def test_load_passing_descarta_cabecera_repetida(tmp_path):
    path = tmp_path / "passing.csv"
    pd.DataFrame(
        {
            "Player": ["A", "Player", "B", None],
            "Pos": ["MF", "Pos", "DF", None],
            "90s": ["10", "90s", "x", None],
            "KP": ["5", "KP", "1", None],
            "PrgP": ["50", "PrgP", "3", None],
        }
    ).to_csv(path, index=False)
    df = load_passing(path)
    assert df["Player"].tolist() == ["A"]
    assert df["90s"].dtype.kind == "f"


def test_load_datos_reales_del_repo(repo_paths):
    assert len(load_pl_tables(repo_paths.pl_tables_csv)) > 600
    assert "Bruno Fernandes" in load_passing(repo_paths.passing_csv)["Player"].tolist()
