"""Configuración central: rutas del proyecto y constantes de dominio.

Ninguna ruta está escrita en duro: todas se derivan de la raíz del proyecto,
que se resuelve desde la ubicación de este archivo o desde la variable de
entorno ``MANUTD_ROOT`` (útil al instalar el paquete fuera del repositorio o al
desplegar en contenedores).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Final

ENV_ROOT: Final[str] = "MANUTD_ROOT"


def _default_root() -> Path:
    """Raíz del repositorio: ``MANUTD_ROOT`` o dos niveles sobre ``src/manutd_analysis``."""
    env_root = os.getenv(ENV_ROOT)
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ProjectPaths:
    """Rutas de entrada y salida del pipeline.

    Parameters
    ----------
    root : Path
        Raíz del proyecto. El resto de las rutas se derivan de ella salvo que
        se indiquen explícitamente (por ejemplo, en tests con ``tmp_path``).
    """

    root: Path

    @property
    def data_dir(self) -> Path:
        return self.root / "data"

    @property
    def export_dir(self) -> Path:
        return self.data_dir / "export"

    @property
    def figures_dir(self) -> Path:
        return self.root / "assets" / "figures"

    @property
    def assets_dir(self) -> Path:
        return self.root / "assets"

    @property
    def docs_dir(self) -> Path:
        return self.root / "docs"

    @property
    def pl_tables_csv(self) -> Path:
        return self.data_dir / PL_TABLES_FILE

    @property
    def passing_csv(self) -> Path:
        return self.data_dir / PASSING_FILE

    @property
    def season_kpis_csv(self) -> Path:
        return self.data_dir / SEASON_KPIS_FILE

    @property
    def readme(self) -> Path:
        return self.root / "README.md"

    @property
    def dashboard_html(self) -> Path:
        return self.root / "dashboard.html"

    @classmethod
    def default(cls) -> ProjectPaths:
        return cls(root=_default_root())


# ── Archivos de datos ─────────────────────────────────────────────────────────
PL_TABLES_FILE: Final[str] = "pl-tables-1993-2024.csv"
PASSING_FILE: Final[str] = "passing_players_2425.csv"
SEASON_KPIS_FILE: Final[str] = "analisis_united_2014_2024.csv"

# ── Dominio ───────────────────────────────────────────────────────────────────
TEAM_NAME: Final[str] = "Manchester Utd"
FIRST_SEASON: Final[int] = 2014
LAST_SEASON: Final[int] = 2024
SEASONS: Final[range] = range(FIRST_SEASON, LAST_SEASON + 1)
TRANSITION_SEPARATOR: Final[str] = "/"

#: Entrenador por año de cierre de temporada (2014 = temporada 2013-14).
#: Las temporadas con relevo a mitad de curso se marcan con "/".
MANAGERS: Final[dict[int, str]] = {
    2014: "David Moyes",
    2015: "Louis van Gaal",
    2016: "Louis van Gaal",
    2017: "José Mourinho",
    2018: "José Mourinho",
    2019: "Mourinho / Solskjær",
    2020: "Ole Gunnar Solskjær",
    2021: "Ole Gunnar Solskjær",
    2022: "Solskjær / Rangnick",
    2023: "Erik ten Hag",
    2024: "Erik ten Hag",
}

TOP_SIX: Final[frozenset[str]] = frozenset(
    {"Manchester Utd", "Liverpool", "Arsenal", "Chelsea", "Manchester City", "Tottenham"}
)

#: Mínimo de minutos para entrar al ranking de pases por 90'.
MIN_MINUTES_PASSING: Final[int] = 900

#: Parámetros del test placebo (cortes aleatorios reproducibles).
PLACEBO_SEED: Final[int] = 42
PLACEBO_SIMULATIONS: Final[int] = 1000
PRE_POST_WINDOW: Final[int] = 3
ALPHA: Final[float] = 0.05
