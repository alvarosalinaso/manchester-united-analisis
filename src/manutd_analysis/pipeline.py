"""Orquestador del pipeline: ingesta → validación → métricas → inferencia → salidas.

Uso::

    python -m manutd_analysis               # pipeline completo
    python -m manutd_analysis --no-sync     # sin reescribir README/dashboard
    python -m manutd_analysis --log-level DEBUG
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from manutd_analysis import cohorts, data_loader, exports, inference, metrics, reporting
from manutd_analysis.config import ProjectPaths
from manutd_analysis.logging_config import setup_logging
from manutd_analysis.validator import SchemaError

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Resultados en memoria de una ejecución del pipeline (útil para tests y la app)."""

    pl_tables: pd.DataFrame
    kpis: pd.DataFrame
    benchmark: pd.DataFrame
    passing: pd.DataFrame
    managers: pd.DataFrame
    findings: dict
    stats: dict
    before_after: dict
    cohorts: dict
    outputs: list[Path] = field(default_factory=list)


def compute(pl_csv: Path | None = None, passing_csv: Path | None = None) -> PipelineResult:
    """Ejecuta ingesta, validación y cálculo sin escribir nada en disco.

    Parameters
    ----------
    pl_csv, passing_csv : Path | None
        Rutas de entrada; por defecto las de :class:`ProjectPaths`.
    """
    pl_tables = data_loader.load_pl_tables(pl_csv)
    passing_raw = data_loader.load_passing(passing_csv)

    kpis = metrics.build_season_kpis(pl_tables)
    benchmark = metrics.league_benchmark(pl_tables)
    findings = metrics.key_findings(kpis, benchmark)
    logger.info(
        "KPIs: %d temporadas | brecha media %.1f pts | costo inestabilidad ~%.1f pts",
        findings["n_temporadas"],
        findings["brecha_media"],
        findings["costo_inestabilidad"],
    )
    return PipelineResult(
        pl_tables=pl_tables,
        kpis=kpis,
        benchmark=benchmark,
        passing=metrics.passing_per_90(passing_raw),
        managers=metrics.manager_summary(kpis),
        findings=findings,
        stats=inference.statistical_tests(kpis),
        before_after=inference.before_after_analysis(kpis),
        cohorts=cohorts.cohort_analysis(kpis),
    )


def write_outputs(
    result: PipelineResult,
    out: ProjectPaths,
    sync_docs: bool = True,
    figures: bool = True,
) -> list[Path]:
    """Persiste todos los artefactos del pipeline bajo ``out``."""
    written: list[Path] = [
        exports.write_csv(result.kpis, out.season_kpis_csv),
        exports.write_csv(result.benchmark, out.export_dir / "pl_benchmark_por_temporada.csv"),
        exports.write_csv(result.passing, out.export_dir / "passing_90_united_2425.csv"),
        exports.write_json(result.findings, out.export_dir / "key_findings.json"),
        exports.write_json(result.stats, out.export_dir / "statistical_tests.json"),
        exports.write_json(result.before_after, out.export_dir / "before_after_analysis.json"),
        exports.write_json(result.cohorts, out.export_dir / "cohort_analysis.json"),
    ]
    written += exports.export_external(
        result.kpis,
        result.pl_tables,
        metrics.group_benchmark(result.pl_tables),
        out.export_dir,
    )

    out.assets_dir.mkdir(parents=True, exist_ok=True)
    table_path = out.assets_dir / "executive_table.html"
    table_path.write_text(reporting.executive_table_html(result.managers), encoding="utf-8")
    written.append(table_path)

    out.docs_dir.mkdir(parents=True, exist_ok=True)
    report_path = out.docs_dir / "paper_report.md"
    report_path.write_text(
        reporting.technical_report(
            result.findings, result.stats, result.before_after, result.cohorts
        ),
        encoding="utf-8",
    )
    written.append(report_path)

    if figures:
        from manutd_analysis import plots

        written += [
            plots.graficar_eficiencia_y_brecha(result.kpis, out.figures_dir),
            plots.graficar_rentabilidad_ofensiva(result.kpis, out.figures_dir),
            plots.graficar_ppg_historico(result.kpis, out.figures_dir),
        ]

    if sync_docs:
        reporting.sync_document(
            out.readme,
            reporting.readme_replacements(
                result.findings,
                result.benchmark,
                result.passing,
                result.managers,
                metrics.stability_comparison(result.kpis),
            ),
        )
        reporting.sync_document(
            out.dashboard_html, reporting.dashboard_replacements(result.findings)
        )

    logger.info("Pipeline completado: %d artefactos escritos", len(written))
    return written


def run(
    out: ProjectPaths | None = None,
    pl_csv: Path | None = None,
    passing_csv: Path | None = None,
    sync_docs: bool = True,
    figures: bool = True,
) -> PipelineResult:
    """Ejecuta el pipeline completo y devuelve los resultados en memoria."""
    result = compute(pl_csv, passing_csv)
    result.outputs = write_outputs(result, out or ProjectPaths.default(), sync_docs, figures)
    return result


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="manutd_analysis",
        description="Pipeline de rendimiento del Manchester United 2014-2024.",
    )
    parser.add_argument("--no-sync", action="store_true", help="No reescribir README/dashboard.")
    parser.add_argument("--no-figures", action="store_true", help="No generar figuras PNG.")
    parser.add_argument("--log-level", default=None, help="DEBUG, INFO, WARNING...")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada de línea de comandos. Devuelve el código de salida."""
    args = _parse_args(argv)
    setup_logging(args.log_level)
    try:
        run(sync_docs=not args.no_sync, figures=not args.no_figures)
    except (data_loader.DataLoadError, SchemaError):
        logger.exception("Datos de entrada inválidos; pipeline abortado")
        return 2
    except OSError:
        logger.exception("Error de E/S al escribir resultados")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
