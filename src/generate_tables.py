"""Genera tabla ejecutiva Man United con fallback a pandas styling"""

from pathlib import Path

import pandas as pd


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

    # Try great_tables first, fallback to pandas styling
    try:
        from great_tables import GT

        tbl = (
            GT(summary.reset_index())
            .tab_header(title="Rendimiento por Entrenador — Man United 2014-2024")
            .tab_source_note("Fuente: FBref/Transfermarkt | Análisis: Álvaro Salinas")
        )
        Path("assets").mkdir(exist_ok=True)
        tbl.save("assets/executive_table.html")
        print("[TABLE] assets/executive_table.html generado (great_tables)")
    except ImportError:
        # Fallback: pandas styling
        styled = (
            summary.reset_index()
            .style.set_caption("Rendimiento por Entrenador — Man United 2014-2024")
            .set_table_styles(
                [
                    {
                        "selector": "caption",
                        "props": [("font-size", "16px"), ("font-weight", "bold")],
                    },
                    {
                        "selector": "th",
                        "props": [
                            ("background-color", "#da020e"),
                            ("color", "white"),
                            ("font-weight", "bold"),
                        ],
                    },
                    {"selector": "td", "props": [("border", "1px solid #ddd")]},
                ]
            )
            .format(precision=1)
            .hide(axis="index")
        )
        Path("assets").mkdir(exist_ok=True)
        styled.to_html("assets/executive_table.html")
        print("[TABLE] assets/executive_table.html generado (pandas styling fallback)")


if __name__ == "__main__":
    generate()
