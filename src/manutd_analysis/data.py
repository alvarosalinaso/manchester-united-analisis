"""Módulo para carga y filtrado de datos del Manchester United."""
from pathlib import Path
from typing import Optional

import pandas as pd

ENTRENADORES: dict[int, str] = {
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

# Columnas requeridas en el CSV de origen
_REQUIRED_COLS = {"team", "season_end_year", "points", "position", "gf", "ga", "played"}


def _resolver_ruta(ruta: str) -> Path:
    """Busca el archivo en CWD y en la raíz del proyecto."""
    candidatos = [
        Path(ruta),
        Path.cwd() / ruta,
        Path(__file__).parent.parent.parent / ruta,  # src/manutd_analysis → project_root
    ]
    for c in candidatos:
        if c.exists():
            return c.resolve()
    raise FileNotFoundError(
        f"No se encontró '{ruta}'. Colócalo en la raíz del proyecto."
    )


def cargar_y_filtrar_datos(
    ruta_archivo: str = "pl-tables-1993-2024.csv",
) -> Optional[pd.DataFrame]:
    """
    Carga el CSV de la Premier League y retorna un DataFrame enriquecido
    con datos del Man Utd (2014-2024) y KPIs calculados.

    Args:
        ruta_archivo: Ruta al CSV fuente.

    Returns:
        DataFrame con columnas: año, pts_utd, pos_utd, gf_utd, ga_utd, played,
        entrenador, pts_champ, gf_champ, ga_champ, brecha_puntos, brecha_ataque,
        brecha_defensa, pts_por_gol, ppg.
        Retorna None si ocurre un error irrecuperable.
    """
    try:
        path = _resolver_ruta(ruta_archivo)
        df = pd.read_csv(path)

        # Validar columnas mínimas
        faltantes = _REQUIRED_COLS - set(df.columns)
        if faltantes:
            raise ValueError(f"El CSV no contiene las columnas: {faltantes}")

        # ── United (2014→2024) ────────────────────────────────────────────────
        mask_utd = (df["team"] == "Manchester Utd") & (df["season_end_year"] >= 2014)
        united = (
            df.loc[mask_utd, ["season_end_year", "points", "position", "gf", "ga", "played"]]
            .copy()
            .rename(
                columns={
                    "season_end_year": "año",
                    "points": "pts_utd",
                    "position": "pos_utd",
                    "gf": "gf_utd",
                    "ga": "ga_utd",
                }
            )
        )
        united["entrenador"] = united["año"].map(ENTRENADORES)

        # ── Campeones ─────────────────────────────────────────────────────────
        campeones = (
            df.loc[df["position"] == 1, ["season_end_year", "points", "gf", "ga"]]
            .rename(
                columns={
                    "season_end_year": "año",
                    "points": "pts_champ",
                    "gf": "gf_champ",
                    "ga": "ga_champ",
                }
            )
        )

        # ── Merge y KPIs ──────────────────────────────────────────────────────
        df_final = pd.merge(united, campeones, on="año", how="inner")
        df_final["brecha_puntos"]  = df_final["pts_champ"]  - df_final["pts_utd"]
        df_final["brecha_ataque"]  = df_final["gf_champ"]   - df_final["gf_utd"]
        df_final["brecha_defensa"] = df_final["ga_utd"]     - df_final["ga_champ"]
        df_final["pts_por_gol"]    = (df_final["pts_utd"] / df_final["gf_utd"]).round(2)
        df_final["ppg"]            = (df_final["pts_utd"] / df_final["played"]).round(3)

        return df_final.reset_index(drop=True)

    except FileNotFoundError as e:
        print(f"❌ Archivo no encontrado: {e}")
    except Exception as e:
        print(f"❌ Error al cargar datos: {e}")

    return None
