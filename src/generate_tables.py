"""Genera tabla ejecutiva Man United con great_tables"""

from pathlib import Path

import pandas as pd
from great_tables import GT


def generate():
    df = pd.read_csv("analisis_united_2014_2024.csv", encoding="utf-8")
    summary = (
        df.groupby("manager")
        .agg(
            temporadas=("season", "count"),
            puntos_promedio=("points", "mean"),
            posicion_media=("position", "mean"),
        )
        .round(1)
        .sort_values("puntos_promedio", ascending=False)
        .head(5)
    )
    summary.columns = ["Temporadas", "Pts/Temporada", "Posición Media"]

    tbl = (
        GT(summary.reset_index())
        .tab_header(title="Rendimiento por Entrenador — Man United 2014-2024")
        .tab_source_note("Fuente: FBref/Transfermarkt | Análisis: Álvaro Salinas")
    )
    Path("assets").mkdir(exist_ok=True)
    tbl.save("assets/executive_table.html")
    print("[TABLE] assets/executive_table.html generado")


if __name__ == "__main__":
    generate()
