"""Módulo de visualización del análisis del Manchester United."""
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

try:
    import seaborn as sns
    sns.set_theme(style="whitegrid", palette="muted")
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False

_DEFAULT_OUT = "assets/figures"
_RED = "#c0392b"
_BLUE = "#2980b9"
_DARK = "#2c3e50"


def _guardar(fig: plt.Figure, nombre: str, out_dir: str) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ruta = out / nombre
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✅ Guardado: {ruta}")
    return ruta


def graficar_eficiencia_y_brecha(
    df: pd.DataFrame, out_dir: str = _DEFAULT_OUT
) -> Path:
    """
    Genera un panel de 2 gráficos:
      - Izquierda: Eficiencia media (Pts/Gol) por entrenador (barras).
      - Derecha:   Brecha de puntos vs. campeón por temporada (línea).
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Manchester United 2014-2024", fontsize=14, fontweight="bold", color=_DARK)

    # ── Eficiencia ────────────────────────────────────────────────────────────
    resumen = df.groupby("entrenador")["pts_por_gol"].mean().sort_values(ascending=False)
    colores = [_RED if v == resumen.max() else _BLUE for v in resumen.values]

    ax1.bar(resumen.index, resumen.values, color=colores, edgecolor="white", linewidth=0.6)
    ax1.set_title("Eficiencia Promedio (Pts / Gol)", fontweight="bold")
    ax1.set_ylabel("Puntos por Gol")
    ax1.tick_params(axis="x", rotation=40)
    ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    ax1.axhline(resumen.mean(), color="gray", linestyle="--", linewidth=0.8, label=f"Media: {resumen.mean():.2f}")
    ax1.legend(fontsize=8)

    # ── Brecha ────────────────────────────────────────────────────────────────
    ax2.plot(df["año"], df["brecha_puntos"], marker="o", color=_RED, linewidth=2, label="Brecha vs. campeón")
    ax2.fill_between(df["año"], df["brecha_puntos"], alpha=0.15, color=_RED)
    ax2.set_title("Brecha de Puntos con el Campeón", fontweight="bold")
    ax2.set_xlabel("Temporada")
    ax2.set_ylabel("Puntos de diferencia")
    ax2.axhline(df["brecha_puntos"].mean(), color="gray", linestyle="--", linewidth=0.8,
                label=f"Media: {df['brecha_puntos'].mean():.1f}")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)

    return _guardar(fig, "eficiencia_y_brecha.png", out_dir)


def graficar_rentabilidad_ofensiva(
    df: pd.DataFrame, out_dir: str = _DEFAULT_OUT
) -> Path:
    """
    Scatter plot: Volumen ofensivo (Goles/temporada) vs. Eficiencia (Pts/Gol)
    con cuadrantes centrados en el promedio grupal.
    """
    fig, ax = plt.subplots(figsize=(10, 7))
    resumen = df.groupby("entrenador").agg(
        gf_utd=("gf_utd", "mean"),
        pts_por_gol=("pts_por_gol", "mean"),
    ).reset_index()

    ax.scatter(resumen["gf_utd"], resumen["pts_por_gol"], s=180, color=_RED, zorder=3, edgecolors=_DARK, linewidth=0.7)

    for _, row in resumen.iterrows():
        ax.annotate(
            row["entrenador"],
            xy=(row["gf_utd"], row["pts_por_gol"]),
            xytext=(6, 4),
            textcoords="offset points",
            fontsize=9,
        )

    media_x = resumen["gf_utd"].mean()
    media_y = resumen["pts_por_gol"].mean()
    ax.axhline(media_y, color="gray", linestyle="--", linewidth=0.8, alpha=0.7)
    ax.axvline(media_x, color="gray", linestyle="--", linewidth=0.8, alpha=0.7)

    # Etiquetas de cuadrantes
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    ax.text(media_x + 0.5, ylim[1] * 0.98, "Alto volumen\nAlta eficiencia", fontsize=7, color="green", va="top")
    ax.text(xlim[0] + 0.3, ylim[1] * 0.98, "Bajo volumen\nAlta eficiencia", fontsize=7, color="gray", va="top")

    ax.set_title("Rentabilidad Ofensiva: Volumen vs. Eficiencia", fontweight="bold")
    ax.set_xlabel("Goles a Favor (promedio por temporada)")
    ax.set_ylabel("Puntos por Gol")
    ax.grid(True, alpha=0.2)

    return _guardar(fig, "rentabilidad_ofensiva.png", out_dir)


def graficar_ppg_historico(
    df: pd.DataFrame, out_dir: str = _DEFAULT_OUT
) -> Path:
    """
    Línea temporal de Puntos por Partido (PPG) con anotación del entrenador.
    """
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df["año"], df["ppg"], marker="o", color=_DARK, linewidth=2)
    ax.fill_between(df["año"], df["ppg"], alpha=0.1, color=_DARK)

    for _, row in df.iterrows():
        ax.annotate(
            row["entrenador"].split("/")[0].strip(),
            xy=(row["año"], row["ppg"]),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            fontsize=7,
            rotation=30,
        )

    ax.set_title("Puntos por Partido (PPG) — Man Utd 2014-2024", fontweight="bold")
    ax.set_xlabel("Temporada")
    ax.set_ylabel("PPG")
    ax.axhline(df["ppg"].mean(), color="gray", linestyle="--", linewidth=0.8,
               label=f"Media período: {df['ppg'].mean():.3f}")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    return _guardar(fig, "ppg_historico.png", out_dir)
