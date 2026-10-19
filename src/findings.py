"""Calcula los hallazgos clave y los sincroniza en README.md y dashboard.html.

Fuente de verdad: el CSV de tablas de la Premier League (pl-tables-1993-2024.csv).
Los números de README.md y dashboard.html se regeneran entre los marcadores
`<!-- FIND:xxx --> ... <!-- /FIND:xxx -->` con `python src/findings.py`.
"""

import json
import re
from pathlib import Path
from typing import Optional

import pandas as pd

from manutd_analysis.analysis import analizar_estabilidad, calcular_costo_inestabilidad
from manutd_analysis.data import cargar_y_filtrar_datos
from src.benchmark_pl import export_benchmark, render_benchmark_table
from src.passing_90 import export_passing_90, render_passing_table


def compute_findings(df: Optional[pd.DataFrame] = None) -> dict:
    """Computa los hallazgos clave a partir de las tablas de la Premier League."""
    if df is None:
        df = cargar_y_filtrar_datos()
        if df is None:
            raise RuntimeError("No se pudo cargar 'pl-tables-1993-2024.csv'")

    # Ranking de DT: solo temporadas con un único entrenador
    # (las temporadas compartidas con '/' se analizan aparte como transiciones)
    df_dt = df[~df["entrenador"].astype(str).str.contains("/", regex=False)]
    per_mgr = df_dt.groupby("entrenador")["ppg"].mean().round(2)
    costo = calcular_costo_inestabilidad(analizar_estabilidad(df))

    return {
        "rango": f"{int(df['año'].min())}-{int(df['año'].max())}",
        "n_temporadas": int(len(df)),
        "brecha_media": round(float(df["brecha_puntos"].mean()), 1),
        "pts_promedio": round(float(df["pts_utd"].mean()), 1),
        "ppg_promedio": round(float(df["ppg"].mean()), 3),
        "mejor_dt": {"nombre": str(per_mgr.idxmax()), "ppg": round(float(per_mgr.max()), 2)},
        "peor_dt": {"nombre": str(per_mgr.idxmin()), "ppg": round(float(per_mgr.min()), 2)},
        "costo_inestabilidad": round(float(costo), 1),
    }


def _findings_table(f: dict) -> str:
    return (
        "| Metric | Value | What it means |\n"
        "|--------|-------|---------------|\n"
        f"| Average gap to champion ({f['rango']}) | {f['brecha_media']:.1f} pts/season "
        "| Points behind the champion on average |\n"
        f"| Best manager (pts/game) | {f['mejor_dt']['nombre']} ({f['mejor_dt']['ppg']:.2f}) "
        "| Highest average PPG while in charge |\n"
        f"| Worst manager (pts/game) | {f['peor_dt']['nombre']} ({f['peor_dt']['ppg']:.2f}) "
        "| Lowest average PPG in the period |\n"
        f"| Cost of instability | ~{f['costo_inestabilidad']:.1f} pts "
        "| Points lost per transition season |"
    )


def _replace_span(text: str, key: str, value: str) -> str:
    pattern = rf"(<!-- FIND:{key} -->).*?(<!-- /FIND:{key} -->)"
    new_text, n = re.subn(pattern, rf"\g<1>{value}\g<2>", text, flags=re.DOTALL)
    if n == 0:
        raise ValueError(f"Marcador <!-- FIND:{key} --> no encontrado")
    return new_text


def sync_findings(data_dir: Path = Path(".")) -> dict:
    """Escribe key_findings.json y actualiza README.md y dashboard.html."""
    findings = compute_findings()
    bench = export_benchmark(data_dir)
    passing = export_passing_90(data_dir)

    output_dir = data_dir / "data" / "export"
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "key_findings.json", "w", encoding="utf-8") as f:
        json.dump(findings, f, ensure_ascii=False, indent=2)

    readme_path = data_dir / "README.md"
    if readme_path.exists():
        text = readme_path.read_text(encoding="utf-8")
        text = _replace_span(text, "table", _findings_table(findings))
        text = _replace_span(text, "brecha", f"{findings['brecha_media']:.1f}")
        if "<!-- FIND:bench -->" in text:
            text = _replace_span(text, "bench", render_benchmark_table(bench))
        if "<!-- FIND:passing -->" in text:
            text = _replace_span(text, "passing", render_passing_table(passing))
        readme_path.write_text(text, encoding="utf-8")

    dashboard_path = data_dir / "dashboard.html"
    if dashboard_path.exists():
        text = dashboard_path.read_text(encoding="utf-8")
        text = _replace_span(text, "brecha", f"{findings['brecha_media']:.1f} pts")
        text = _replace_span(text, "costo", f"~{findings['costo_inestabilidad']:.1f} pts")
        dashboard_path.write_text(text, encoding="utf-8")

    print(
        f"[FINDINGS] brecha={findings['brecha_media']:.1f} | "
        f"mejor={findings['mejor_dt']['nombre']} ({findings['mejor_dt']['ppg']:.2f}) | "
        f"peor={findings['peor_dt']['nombre']} ({findings['peor_dt']['ppg']:.2f})"
    )
    return findings


if __name__ == "__main__":
    sync_findings()
