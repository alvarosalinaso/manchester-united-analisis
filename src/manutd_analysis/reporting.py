"""Capa de presentación: tablas Markdown/HTML, informe técnico y sincronización del README.

Los números publicados en ``README.md`` y ``dashboard.html`` se regeneran
entre marcadores ``<!-- FIND:clave --> ... <!-- /FIND:clave -->``, de modo que
la documentación nunca diverge de lo que calcula el pipeline.
"""

from __future__ import annotations

import logging
import re
from datetime import date
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class MarkerNotFoundError(ValueError):
    """El documento no contiene el marcador ``<!-- FIND:clave -->`` esperado."""


# ── Tablas Markdown ───────────────────────────────────────────────────────────


def findings_table(f: dict) -> str:
    """Tabla Markdown de hallazgos clave."""
    rows = [
        "| Métrica | Valor | Lectura de negocio |",
        "|---------|-------|--------------------|",
        f"| Brecha media vs campeón ({f['rango']}) | **{f['brecha_media']:.1f} pts/temporada** "
        f"| Rango {f['brecha_min']}–{f['brecha_max']} pts; ninguna temporada en disputa real del título |",
        f"| PPG United vs PPG campeón | {f['ppg_promedio']:.2f} vs {f['ppg_campeon_promedio']:.2f} "
        "| Diferencia estructural, no coyuntural |",
        f"| Mejor entrenador (PPG) | {f['mejor_dt']['nombre']} ({f['mejor_dt']['ppg']:.2f}) "
        "| Máximo rendimiento por partido en temporadas completas |",
        f"| Peor entrenador (PPG) | {f['peor_dt']['nombre']} ({f['peor_dt']['ppg']:.2f}) "
        "| Mínimo del período |",
        f"| Costo de la inestabilidad | **~{f['costo_inestabilidad']:.1f} pts** "
        f"| Puntos perdidos en cada temporada con relevo de DT ({f['n_temporadas_transicion']} casos) |",
        f"| Temporadas en Top 4 | {f['temporadas_top4']} de {f['n_temporadas']} "
        "| Acceso a Champions League no garantizado |",
    ]
    if "ventaja_ppg_vs_pl" in f:
        rows.append(
            f"| Ventaja PPG vs media PL (sin United) | {f['ventaja_ppg_vs_pl']:+.2f} "
            "| Sigue sobre la media de la liga: el problema es la élite, no la liga |"
        )
    return "\n".join(rows)


def benchmark_table(bench: pd.DataFrame) -> str:
    """Tabla Markdown del benchmark United vs media PL por temporada."""
    lines = [
        "| Temporada | PPG United | PPG media PL (sin United) | Δ PPG |",
        "|-----------|------------|---------------------------|-------|",
    ]
    lines += [
        f"| {int(r.temporada)} | {r.united_ppg:.2f} | {r.pl_avg_ppg_sin_utd:.2f} | {r.diff_ppg_vs_pl:+.2f} |"
        for r in bench.itertuples(index=False)
    ]
    return "\n".join(lines)


def passing_table(tabla: pd.DataFrame) -> str:
    """Tabla Markdown de pases por 90 minutos."""
    lines = [
        "| Jugador | Pos | 90s | PrgP/90 | KP/90 | Pctl PrgP (plantel) | Pctl KP (plantel) |",
        "|---------|-----|-----|---------|-------|---------------------|-------------------|",
    ]
    lines += [
        f"| {r.jugador} | {r.pos} | {r.min_90s:.1f} | {r.prgp_90:.2f} | {r.kp_90:.2f} "
        f"| {r.pct_prgp_plantel} | {r.pct_kp_plantel} |"
        for r in tabla.itertuples(index=False)
    ]
    return "\n".join(lines)


def manager_table(summary: pd.DataFrame) -> str:
    """Tabla Markdown de rendimiento por entrenador."""
    lines = [
        "| Entrenador | Temporadas | Pts/temporada | Posición media | PPG | Brecha vs campeón |",
        "|------------|------------|---------------|----------------|-----|-------------------|",
    ]
    lines += [
        f"| {name} | {int(r.temporadas)} | {r.pts_promedio:.1f} | {r.posicion_media:.1f} "
        f"| {r.ppg:.2f} | {r.brecha_vs_campeon:.1f} |"
        for name, r in summary.iterrows()
    ]
    return "\n".join(lines)


def stability_table(comparison: pd.DataFrame) -> str:
    """Tabla Markdown comparando temporadas estables vs temporadas con relevo de DT."""
    lines = [
        "| Escenario | Pts/temporada | PPG | Goles a favor | Brecha vs campeón |",
        "|-----------|---------------|-----|---------------|-------------------|",
    ]
    lines += [
        f"| {name} | {r.pts_utd:.1f} | {r.ppg:.2f} | {r.gf_utd:.1f} | {r.brecha_puntos:.1f} |"
        for name, r in comparison.iterrows()
    ]
    return "\n".join(lines)


# ── Sincronización de documentos ──────────────────────────────────────────────


def replace_marker(text: str, key: str, value: str) -> str:
    """Reemplaza el contenido entre ``<!-- FIND:key -->`` y ``<!-- /FIND:key -->``.

    Raises
    ------
    MarkerNotFoundError
        Si el marcador no existe en ``text``.
    """
    pattern = rf"(<!-- FIND:{re.escape(key)} -->).*?(<!-- /FIND:{re.escape(key)} -->)"
    new_text, n = re.subn(
        pattern, lambda m: f"{m.group(1)}{value}{m.group(2)}", text, flags=re.DOTALL
    )
    if n == 0:
        raise MarkerNotFoundError(f"Marcador <!-- FIND:{key} --> no encontrado")
    return new_text


def sync_document(path: Path, replacements: dict[str, str]) -> bool:
    """Aplica ``replacements`` a los marcadores presentes en ``path``.

    Los marcadores ausentes se omiten con un aviso; el archivo solo se
    reescribe si su contenido cambia.

    Returns
    -------
    bool
        ``True`` si el archivo se modificó.
    """
    if not path.is_file():
        logger.warning("No existe %s; se omite la sincronización", path)
        return False
    original = path.read_text(encoding="utf-8")
    text = original
    for key, value in replacements.items():
        try:
            text = replace_marker(text, key, value)
        except MarkerNotFoundError:
            logger.debug("%s no tiene el marcador '%s'", path.name, key)
    if text == original:
        return False
    path.write_text(text, encoding="utf-8")
    logger.info("Sincronizado: %s", path)
    return True


def readme_replacements(
    findings: dict,
    bench: pd.DataFrame,
    passing: pd.DataFrame,
    managers: pd.DataFrame,
    comparison: pd.DataFrame,
) -> dict[str, str]:
    """Valores a inyectar en los marcadores del README."""
    return {
        "table": findings_table(findings),
        "brecha": f"{findings['brecha_media']:.1f}",
        "costo": f"{findings['costo_inestabilidad']:.1f}",
        "bench": benchmark_table(bench),
        "passing": passing_table(passing),
        "managers": manager_table(managers),
        "stability": stability_table(comparison),
    }


def dashboard_replacements(findings: dict) -> dict[str, str]:
    """Valores a inyectar en los KPIs de ``dashboard.html``."""
    return {
        "brecha": f"{findings['brecha_media']:.1f} pts",
        "costo": f"~{findings['costo_inestabilidad']:.1f} pts",
    }


# ── Tabla ejecutiva HTML ──────────────────────────────────────────────────────


def executive_table_html(summary: pd.DataFrame, top_n: int = 5) -> str:
    """Tabla ejecutiva por entrenador en HTML (great_tables, sin navegador)."""
    from great_tables import GT

    data = (
        summary[["temporadas", "pts_promedio", "posicion_media"]]
        .head(top_n)
        .round(1)
        .rename(
            columns={
                "temporadas": "Temporadas",
                "pts_promedio": "Pts/Temporada",
                "posicion_media": "Posición Media",
            }
        )
        .reset_index(names="Entrenador")
    )
    return (
        GT(data, id="manutd-executive-table")
        .tab_header(title="Rendimiento por entrenador, Man United 2014-2024")
        .tab_source_note("Fuente: tablas finales de la Premier League | Análisis: Álvaro Salinas")
        .as_raw_html()
    )


# ── Informe técnico ───────────────────────────────────────────────────────────


def technical_report(findings: dict, stats: dict, before_after: dict, cohorts: dict) -> str:
    """Informe técnico en Markdown construido solo a partir de resultados calculados."""
    f = findings
    lines = [
        "# Manchester United 2014-2024: costo de la inestabilidad técnica",
        "",
        f"**Autor:** Álvaro Salinas Ortiz · **Generado:** {date.today().isoformat()} · "
        "**Repositorio:** https://github.com/alvarosalinaso/manchester-united-analisis",
        "",
        "## Resumen ejecutivo",
        "",
        f"- En {f['n_temporadas']} temporadas ({f['rango']}) el United terminó en promedio "
        f"**{f['brecha_media']:.1f} puntos** detrás del campeón (rango {f['brecha_min']}–{f['brecha_max']}).",
        f"- Las {f['n_temporadas_transicion']} temporadas con relevo de entrenador rindieron "
        f"**~{f['costo_inestabilidad']:.1f} puntos menos** que las temporadas con un único DT.",
        f"- PPG por entrenador (temporadas completas): máximo {f['mejor_dt']['nombre']} "
        f"({f['mejor_dt']['ppg']:.2f}), mínimo {f['peor_dt']['nombre']} ({f['peor_dt']['ppg']:.2f}).",
        "",
        "## Datos y método",
        "",
        "- Fuente: tablas finales de la Premier League 1993-2024 (20 equipos por temporada).",
        "- Pipeline: ingesta tipada → validación de esquema fail-fast → métricas puras → exportación.",
        "- Contrastes: Pearson, Welch y Mann-Whitney (α = 0.05); comparación pre/post de cada "
        "cambio de DT con test placebo de cortes aleatorios (semilla fija).",
        "",
        "## Contrastes estadísticos",
        "",
        "| Test | Estadístico | p-valor | Significativo |",
        "|------|-------------|---------|---------------|",
    ]
    for name, block in stats.items():
        stat_key = next(k for k in ("r", "t_statistic", "u_statistic") if k in block)
        lines.append(
            f"| {name} | {stat_key}={block[stat_key]} | {block['p_value']:.4f} "
            f"| {'sí' if block['significant'] else 'no'} |"
        )

    lines += ["", "## Cambios de entrenador (pre/post, descriptivo)", ""]
    placebo = before_after.get("placebo_test", {})
    if placebo:
        lines += [
            "| Cambio | Temporada | Δ pts (3 temp. post − pre) | p placebo |",
            "|--------|-----------|-----------------------------|-----------|",
        ]
        lines += [
            f"| {c['change']} | {c['season']} | {c['delta_points']:+.1f} | {c['p_value_placebo']:.3f} |"
            for c in placebo["per_change"]
        ]
        lines.append("")
        lines.append(f"> {placebo['interpretation']}.")

    summary = cohorts.get("tenure_summary", {})
    if summary:
        lines += [
            "",
            "## Cohortes por entrenador",
            "",
            f"- {summary['n_managers']} cohortes (incluye temporadas compartidas); tenencia media "
            f"{summary['avg_tenure']} temporadas; rotación {summary['turnover_rate']} "
            f"{summary['turnover_rate_unit']}.",
            f"- Mayor tenencia: {summary['longest_tenure']['manager']} "
            f"({summary['longest_tenure']['seasons']} temporadas).",
        ]

    lines += [
        "",
        "## Limitaciones",
        "",
        "- La comparación pre/post no identifica efectos causales (sin grupo control).",
        "- No se modela gasto en fichajes ni valor de plantilla (sin fuente fiable).",
        "",
        "---",
        "*Generado automáticamente por `python -m manutd_analysis`.*",
        "",
    ]
    return "\n".join(lines)
