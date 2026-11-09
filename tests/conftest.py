"""Fixtures compartidas: datos sintéticos mínimos y rutas reales del repositorio."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd
import pytest

matplotlib.use("Agg")

from manutd_analysis.config import SEASONS, TEAM_NAME, ProjectPaths  # noqa: E402

REPO = ProjectPaths(root=Path(__file__).resolve().parents[1])


@pytest.fixture
def repo_paths() -> ProjectPaths:
    return REPO


@pytest.fixture
def synthetic_pl() -> pd.DataFrame:
    """Tablas PL sintéticas 2014-2024: campeón, United y un tercer equipo por temporada."""
    rows = []
    for i, season in enumerate(SEASONS):
        base = {"season_end_year": season, "played": 38}
        rows += [
            {
                **base,
                "team": "Champion FC",
                "position": 1,
                "won": 28,
                "gf": 90,
                "ga": 30,
                "points": 90,
            },
            {
                **base,
                "team": TEAM_NAME,
                "position": 4 + (i % 3),
                "won": 20,
                "gf": 60 + i,
                "ga": 40,
                "points": 70 - i,
            },
            {
                **base,
                "team": "Other FC",
                "position": 10,
                "won": 12,
                "gf": 45,
                "ga": 50,
                "points": 45,
            },
        ]
    return pd.DataFrame(rows)


@pytest.fixture
def synthetic_pl_csv(tmp_path, synthetic_pl) -> Path:
    path = tmp_path / "pl.csv"
    synthetic_pl.to_csv(path, index=False)
    return path


@pytest.fixture
def kpis(synthetic_pl) -> pd.DataFrame:
    from manutd_analysis.metrics import build_season_kpis

    return build_season_kpis(synthetic_pl)
