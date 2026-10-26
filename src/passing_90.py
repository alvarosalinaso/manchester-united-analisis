"""Métricas de pase por 90 minutos (2024-25), plantel del Manchester United.

Fuente de datos: `data/passing_players_2425.csv`, exportación de FBref del
repositorio united-passing-efficiency-24-25 (solo lectura allí).

- Filtro: mínimo 900 minutos jugados (columna `90s` >= 10).
- Métricas: PrgP/90 (pases progresivos) y KP/90 (pases clave), columna FBref `PrgP`, no `Prog`.
- Percentiles: dentro del plantel del United (FBref bloquea el acceso automatizado
  a la tabla completa de la liga; no se inventan percentiles de liga).
- NO incluye red de pases ni xT.
"""

from pathlib import Path
from typing import Optional

import pandas as pd

MIN_MINUTOS = 900
MIN_90S = MIN_MINUTOS / 90  # 10.0


def _resolver_csv(ruta: Optional[Path] = None) -> Path:
    if ruta is not None:
        return ruta
    candidatos = [
        Path("data/passing_players_2425.csv"),
        Path(__file__).resolve().parent.parent / "data" / "passing_players_2425.csv",
    ]
    for c in candidatos:
        if c.exists():
            return c
    raise FileNotFoundError("No se encontró 'data/passing_players_2425.csv'")


def compute_passing_90(ruta: Optional[Path] = None) -> pd.DataFrame:
    """PrgP/90 y KP/90 con percentil de plantel para jugadores con ≥900 minutos."""
    df = pd.read_csv(_resolver_csv(ruta))
    # La exportación de FBref incluye una fila de cabecera repetida
    df = df[df["Player"].notna() & (df["Player"] != "Player")].copy()
    for col in ["90s", "KP", "PrgP"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["90s", "KP", "PrgP"])
    df = df[df["90s"] >= MIN_90S].copy()

    df["prgp_90"] = (df["PrgP"] / df["90s"]).round(2)
    df["kp_90"] = (df["KP"] / df["90s"]).round(2)
    df["pct_prgp_plantel"] = (df["prgp_90"].rank(pct=True) * 100).round(0).astype(int)
    df["pct_kp_plantel"] = (df["kp_90"].rank(pct=True) * 100).round(0).astype(int)

    columnas = [
        "Player",
        "Pos",
        "90s",
        "PrgP",
        "KP",
        "prgp_90",
        "kp_90",
        "pct_prgp_plantel",
        "pct_kp_plantel",
    ]
    return (
        df[columnas]
        .sort_values("prgp_90", ascending=False)
        .reset_index(drop=True)
        .rename(
            columns={
                "Player": "jugador",
                "Pos": "pos",
                "90s": "min_90s",
                "PrgP": "prgp",
                "KP": "kp",
            }
        )
    )


def render_passing_table(tabla: pd.DataFrame) -> str:
    """Tabla markdown de passing por 90' para el README."""
    lineas = [
        "| Jugador | Pos | 90s | PrgP/90 | KP/90 | Pctl PrgP (plantel) | Pctl KP (plantel) |",
        "|---------|-----|-----|---------|-------|---------------------|-------------------|",
    ]
    for row in tabla.itertuples(index=False):
        lineas.append(
            f"| {row.jugador} | {row.pos} | {row.min_90s:.1f} | {row.prgp_90:.2f} "
            f"| {row.kp_90:.2f} | {row.pct_prgp_plantel} | {row.pct_kp_plantel} |"
        )
    return "\n".join(lineas)


def export_passing_90(data_dir: Path = Path(".")) -> pd.DataFrame:
    """Escribe data/export/passing_90_united_2425.csv y retorna la tabla."""
    tabla = compute_passing_90()
    output_dir = data_dir / "data" / "export"
    output_dir.mkdir(parents=True, exist_ok=True)
    ruta = output_dir / "passing_90_united_2425.csv"
    tabla.to_csv(ruta, index=False)
    print(f"[PASSING] {len(tabla)} jugadores con ≥{MIN_MINUTOS} minutos exportados a {ruta}")
    return tabla
