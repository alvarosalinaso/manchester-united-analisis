"""Benchmark: promedio de la Premier League sin el Manchester United por temporada.

Fuente: pl-tables-1993-2024.csv (CSV del repositorio con las tablas finales de
todas las temporadas de la Premier League, incluyendo los 20 equipos de cada una).
"""

from pathlib import Path
from typing import Optional

import pandas as pd

from manutd_analysis.data import _resolver_ruta

TEMPORADAS = range(2014, 2025)


def compute_benchmark(ruta: Optional[Path] = None) -> pd.DataFrame:
    """PPG del United vs media de la PL sin United, por temporada (2014-2024)."""
    path = ruta if ruta is not None else _resolver_ruta("pl-tables-1993-2024.csv")
    df = pd.read_csv(path)
    df = df[df["season_end_year"].isin(TEMPORADAS)].copy()
    df["ppg"] = df["points"] / df["played"]

    filas = []
    for temporada, grupo in df.groupby("season_end_year"):
        utd = grupo[grupo["team"] == "Manchester Utd"]
        resto = grupo[grupo["team"] != "Manchester Utd"]
        if utd.empty or resto.empty:
            continue
        ppg_utd = float(utd["ppg"].iloc[0])
        ppg_pl = float(resto["ppg"].mean())
        filas.append(
            {
                "temporada": int(temporada),
                "united_pts": int(utd["points"].iloc[0]),
                "united_ppg": round(ppg_utd, 3),
                "pl_avg_pts_sin_utd": round(float(resto["points"].mean()), 1),
                "pl_avg_ppg_sin_utd": round(ppg_pl, 3),
                "diff_ppg_vs_pl": round(ppg_utd - ppg_pl, 3),
            }
        )
    return pd.DataFrame(filas).sort_values("temporada").reset_index(drop=True)


def render_benchmark_table(bench: pd.DataFrame) -> str:
    """Tabla markdown del benchmark para el README."""
    lineas = [
        "| Season | United PPG | PL avg PPG (sin United) | Δ PPG |",
        "|--------|------------|--------------------------|-------|",
    ]
    for row in bench.itertuples(index=False):
        lineas.append(
            f"| {int(row.temporada)} | {row.united_ppg:.2f} "
            f"| {row.pl_avg_ppg_sin_utd:.2f} | {row.diff_ppg_vs_pl:+.2f} |"
        )
    return "\n".join(lineas)


def export_benchmark(data_dir: Path = Path(".")) -> pd.DataFrame:
    """Escribe data/export/pl_benchmark_por_temporada.csv y retorna el DataFrame."""
    bench = compute_benchmark()
    output_dir = data_dir / "data" / "export"
    output_dir.mkdir(parents=True, exist_ok=True)
    ruta = output_dir / "pl_benchmark_por_temporada.csv"
    bench.to_csv(ruta, index=False)
    media_diff = bench["diff_ppg_vs_pl"].mean()
    print(f"[BENCH] {len(bench)} temporadas exportadas a {ruta} (Δ PPG media: {media_diff:+.3f})")
    return bench
