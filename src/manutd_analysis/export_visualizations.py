"""Exportación de visualizaciones para plataformas externas (Datawrapper, Flourish, Observable)."""

from pathlib import Path

import pandas as pd

from manutd_analysis.data import cargar_y_filtrar_datos

# ── Constantes ────────────────────────────────────────────────────────────────
_EXPORT_DIR = Path("data/export")
_TOP_SIX: set[str] = {
    "Manchester Utd",
    "Liverpool",
    "Arsenal",
    "Chelsea",
    "Manchester City",
    "Tottenham",
}


# ── Funciones de generación de CSV ───────────────────────────────────────────


def _crear_dir_export() -> None:
    """Crea el directorio de exportación si no existe."""
    _EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def _cargar_datos_completos() -> pd.DataFrame:
    """Carga los datos completos de la Premier League para benchmarking."""
    path = Path("pl-tables-1993-2024.csv")
    try:
        return pd.read_csv(path)
    except FileNotFoundError as err:
        raise FileNotFoundError(
            "No se encontró 'pl-tables-1993-2024.csv' en la raíz del proyecto."
        ) from err


def generar_benchmark_pl(df_completo: pd.DataFrame, temporadas: range = range(2014, 2025)) -> Path:
    """
    Genera CSV para Datawrapper: PPG promedio de Man Utd vs Top 6 vs Resto PL.

    Args:
        df_completo: DataFrame completo de la Premier League.
        temporadas: Rango de temporadas a incluir.

    Returns:
        Ruta del archivo CSV generado.
    """
    _crear_dir_export()
    df = df_completo[df_completo["season_end_year"].isin(temporadas)].copy()
    df["ppg"] = (df["points"] / df["played"]).round(3)

    # Clasificar equipos
    def clasificar_equipo(team: str) -> str:
        if team == "Manchester Utd":
            return "Manchester Utd"
        elif team in _TOP_SIX:
            return "Top 6 (sin Utd)"
        return "Resto PL"

    df["grupo"] = df["team"].apply(clasificar_equipo)

    # Calcular PPG promedio por grupo
    benchmark = (
        df.groupby("grupo")["ppg"]
        .mean()
        .reset_index()
        .rename(columns={"grupo": "Grupo", "ppg": "PPG_Promedio"})
        .sort_values("PPG_Promedio", ascending=False)
    )

    ruta = _EXPORT_DIR / "dw_benchmark_pl.csv"
    benchmark.to_csv(ruta, index=False)
    print(f"  ✅ Benchmark PL exportado: {ruta}")
    return ruta


def generar_bump_manager(df: pd.DataFrame) -> Path:
    """
    Genera CSV para Flourish bump chart: posición del Man Utd por temporada y entrenador.

    Args:
        df: DataFrame maestro de Man Utd (2014-2024).

    Returns:
        Ruta del archivo CSV generado.
    """
    _crear_dir_export()
    bump = (
        df[["año", "pos_utd", "entrenador", "ppg"]]
        .copy()
        .rename(
            columns={
                "año": "Season",
                "pos_utd": "Position",
                "entrenador": "Manager",
                "ppg": "PPG",
            }
        )
        .sort_values("Season")
    )

    ruta = _EXPORT_DIR / "flourish_bump_manager.csv"
    bump.to_csv(ruta, index=False)
    print(f"  ✅ Bump chart exportado: {ruta}")
    return ruta


def generar_correlacion(df: pd.DataFrame) -> Path:
    """
    Genera CSV para Observable Plot: datos de correlación (points, GF, GA, GD, wins, position).

    Args:
        df: DataFrame maestro de Man Utd (2014-2024).

    Returns:
        Ruta del archivo CSV generado.
    """
    _crear_dir_export()
    corr = df[["año", "pts_utd", "gf_utd", "ga_utd", "pos_utd", "entrenador"]].copy()
    corr["gd"] = corr["gf_utd"] - corr["ga_utd"]
    corr["wins"] = ((corr["pts_utd"] - (corr["gf_utd"] - corr["ga_utd"])) / 3).round(0).astype(int)
    corr = corr.rename(
        columns={
            "año": "Season",
            "pts_utd": "Points",
            "gf_utd": "Goals_For",
            "ga_utd": "Goals_Against",
            "pos_utd": "Position",
            "gd": "Goal_Difference",
            "wins": "Wins",
        }
    )

    ruta = _EXPORT_DIR / "observable_correlacion.csv"
    corr.to_csv(ruta, index=False)
    print(f"  ✅ Correlación exportada: {ruta}")
    return ruta


def generar_html_snippets() -> Path:
    """
    Genera snippets HTML responsivos para embeber las visualizaciones.

    Returns:
        Ruta del archivo Markdown generado.
    """
    _crear_dir_export()
    snippets = """# Embed Snippets — Visualizaciones Man Utd

## 1. Datawrapper: Benchmark PL (PPG Comparison)

```html
<div style="width: 100%; max-width: 800px; margin: 0 auto;">
  <iframe
    src="https://www.datawrapper.dw-news.net/DATASET_ID/"
    title="Benchmark PL — Man Utd PPG vs Top 6 vs Rest"
    width="100%"
    height="400"
    frameborder="0"
    allow="fullscreen"
    loading="lazy"
  ></iframe>
  <noscript>
    <p>Ver <a href="data/export/dw_benchmark_pl.csv">datos del benchmark</a>.</p>
  </noscript>
</div>
```

**Archivo de datos:** `data/export/dw_benchmark_pl.csv`

---

## 2. Flourish: Bump Chart (Manager Timeline)

```html
<div style="width: 100%; max-width: 900px; margin: 0 auto;">
  <iframe
    src="https://flo.uri.sh/visualisation/VISUALISATION_ID/embed"
    title="Bump Chart — Manager Performance Timeline"
    width="100%"
    height="500"
    frameborder="0"
    allow="fullscreen"
    loading="lazy"
  ></iframe>
  <noscript>
    <p>Ver <a href="data/export/flourish_bump_manager.csv">datos del bump chart</a>.</p>
  </noscript>
</div>
```

**Archivo de datos:** `data/export/flourish_bump_manager.csv`

---

## 3. Observable Plot: Correlation Matrix

```html
<div style="width: 100%; max-width: 800px; margin: 0 auto;">
  <iframe
    src="https://observablehq.com/@observablehq/MANU_CORRELACION_ID"
    title="Correlation Matrix — Points, GF, GA, GD, Wins, Position"
    width="100%"
    height="600"
    frameborder="0"
    allow="fullscreen"
    loading="lazy"
  ></iframe>
  <noscript>
    <p>Ver <a href="data/export/observable_correlacion.csv">datos de correlación</a>.</p>
  </noscript>
</div>
```

**Archivo de datos:** `data/export/observable_correlacion.csv`

---

*Generado por `manutd_analysis.export_visualizations`.*
"""
    ruta = _EXPORT_DIR / "embed_snippets.md"
    ruta.write_text(snippets, encoding="utf-8")
    print(f"  ✅ Embed snippets exportado: {ruta}")
    return ruta


# ── Función principal ─────────────────────────────────────────────────────────


def main() -> None:
    """Genera todos los archivos de exportación para visualizaciones."""
    print("📊 Iniciando exportación de visualizaciones...")

    # Cargar datos
    df = cargar_y_filtrar_datos()
    if df is None:
        print("❌ No se pudieron cargar los datos. Abortando.")
        return

    df_completo = _cargar_datos_completos()

    # Generar CSVs
    generar_benchmark_pl(df_completo)
    generar_bump_manager(df)
    generar_correlacion(df)

    # Generar snippets HTML
    generar_html_snippets()

    print("\n✅ Exportación completada.")


if __name__ == "__main__":
    main()
