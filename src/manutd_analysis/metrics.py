"""Métricas de negocio: funciones puras sobre DataFrames ya validados.

Ninguna función de este módulo lee ni escribe archivos ni muta su entrada.
Toda división pasa por :func:`safe_divide`, que convierte denominadores cero en
``NaN`` en vez de producir ``inf`` o lanzar excepciones.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from manutd_analysis.config import (
    MANAGERS,
    MIN_MINUTES_PASSING,
    SEASONS,
    TEAM_NAME,
    TOP_SIX,
    TRANSITION_SEPARATOR,
)
from manutd_analysis.validator import require_columns, validate_season_kpis

STABLE_LABEL = "Estable (1 Técnico)"
TRANSITION_LABEL = "Transición (Relevo)"


def safe_divide(
    numerator: pd.Series | float,
    denominator: pd.Series,
    fill_value: float | None = None,
) -> pd.Series:
    """Divide evitando ``inf`` cuando el denominador es cero.

    Parameters
    ----------
    numerator : pd.Series | float
        Numerador.
    denominator : pd.Series
        Denominador; los ceros se reemplazan por ``NaN`` antes de dividir.
    fill_value : float | None
        Si se indica, los ``NaN`` del resultado se rellenan con este valor.
        Por defecto se mantienen como ``NaN`` para no inventar métricas.

    Returns
    -------
    pd.Series
        Resultado de la división, tipo ``float64``.

    Examples
    --------
    >>> safe_divide(pd.Series([10, 5]), pd.Series([2, 0])).tolist()
    [5.0, nan]
    """
    result = numerator / denominator.astype("float64").replace(0, np.nan)
    if fill_value is not None:
        result = result.fillna(fill_value)
    return result.astype("float64")


def is_transition(managers: pd.Series) -> pd.Series:
    """Marca temporadas con relevo de entrenador (nombre con ``/``)."""
    return managers.astype(str).str.contains(TRANSITION_SEPARATOR, regex=False)


# ── KPIs por temporada ────────────────────────────────────────────────────────


def build_season_kpis(pl_tables: pd.DataFrame) -> pd.DataFrame:
    """Construye la tabla maestra de KPIs del United frente al campeón (2014-2024).

    Parameters
    ----------
    pl_tables : pd.DataFrame
        Tablas finales de la Premier League, ya validadas por
        :func:`manutd_analysis.data_loader.load_pl_tables`.

    Returns
    -------
    pd.DataFrame
        Una fila por temporada con: ``año``, ``pts_utd``, ``pos_utd``,
        ``gf_utd``, ``ga_utd``, ``played``, ``entrenador``, ``pts_champ``,
        ``gf_champ``, ``ga_champ``, ``brecha_puntos`` (pts del campeón − pts del
        United), ``brecha_ataque`` (goles del campeón − goles del United),
        ``brecha_defensa`` (goles recibidos United − campeón), ``pts_por_gol``,
        ``ppg`` (puntos por partido) y ``es_transicion``.
    """
    in_period = pl_tables["season_end_year"].isin(SEASONS)
    united = (
        pl_tables.loc[
            in_period & (pl_tables["team"] == TEAM_NAME),
            ["season_end_year", "points", "position", "gf", "ga", "played"],
        ]
        .rename(
            columns={
                "season_end_year": "año",
                "points": "pts_utd",
                "position": "pos_utd",
                "gf": "gf_utd",
                "ga": "ga_utd",
            }
        )
        .copy()
    )
    united["entrenador"] = united["año"].map(MANAGERS)

    champions = pl_tables.loc[
        in_period & (pl_tables["position"] == 1), ["season_end_year", "points", "gf", "ga"]
    ].rename(
        columns={
            "season_end_year": "año",
            "points": "pts_champ",
            "gf": "gf_champ",
            "ga": "ga_champ",
        }
    )

    kpis = united.merge(champions, on="año", how="inner", validate="one_to_one")
    kpis["brecha_puntos"] = kpis["pts_champ"] - kpis["pts_utd"]
    kpis["brecha_ataque"] = kpis["gf_champ"] - kpis["gf_utd"]
    kpis["brecha_defensa"] = kpis["ga_utd"] - kpis["ga_champ"]
    kpis["pts_por_gol"] = safe_divide(kpis["pts_utd"], kpis["gf_utd"]).round(2)
    kpis["ppg"] = safe_divide(kpis["pts_utd"], kpis["played"]).round(3)
    kpis["es_transicion"] = is_transition(kpis["entrenador"])
    kpis = kpis.sort_values("año").reset_index(drop=True)
    return validate_season_kpis(kpis)


# ── Rendimiento por entrenador ────────────────────────────────────────────────


def efficiency_by_manager(kpis: pd.DataFrame) -> pd.Series:
    """Puntos por gol medios por entrenador, de mayor a menor."""
    require_columns(kpis, {"entrenador", "pts_por_gol"}, "efficiency_by_manager")
    return kpis.groupby("entrenador")["pts_por_gol"].mean().sort_values(ascending=False).round(3)


def ppg_by_manager(kpis: pd.DataFrame, exclude_transitions: bool = True) -> pd.Series:
    """PPG medio por entrenador.

    Parameters
    ----------
    kpis : pd.DataFrame
        Tabla de :func:`build_season_kpis`.
    exclude_transitions : bool
        Si es ``True`` (por defecto) se excluyen las temporadas compartidas
        entre dos entrenadores, para no atribuir el resultado a ninguno.
    """
    require_columns(kpis, {"entrenador", "ppg"}, "ppg_by_manager")
    data = kpis[~is_transition(kpis["entrenador"])] if exclude_transitions else kpis
    return data.groupby("entrenador")["ppg"].mean().round(2).sort_values(ascending=False)


def stability_comparison(kpis: pd.DataFrame) -> pd.DataFrame:
    """Compara medias de temporadas estables frente a temporadas de relevo.

    Returns
    -------
    pd.DataFrame
        Índice ``STABLE_LABEL`` / ``TRANSITION_LABEL`` (solo los presentes) y
        columnas ``pts_utd``, ``brecha_puntos``, ``gf_utd``, ``ppg``.
    """
    cols = ["pts_utd", "brecha_puntos", "gf_utd", "ppg"]
    require_columns(kpis, {"entrenador", *cols}, "stability_comparison")
    labels = is_transition(kpis["entrenador"]).map({False: STABLE_LABEL, True: TRANSITION_LABEL})
    comparison = kpis[cols].groupby(labels).mean().round(2)
    comparison.index.name = None
    return comparison.reindex(
        [i for i in (STABLE_LABEL, TRANSITION_LABEL) if i in comparison.index]
    )


def instability_cost(comparison: pd.DataFrame) -> float:
    """Puntos perdidos en una temporada de relevo frente a una estable.

    Returns
    -------
    float
        ``pts estable − pts transición``. ``NaN`` si falta alguno de los grupos.
    """
    if STABLE_LABEL not in comparison.index or TRANSITION_LABEL not in comparison.index:
        return float("nan")
    return float(
        comparison.loc[STABLE_LABEL, "pts_utd"] - comparison.loc[TRANSITION_LABEL, "pts_utd"]
    )


def manager_summary(kpis: pd.DataFrame) -> pd.DataFrame:
    """Tabla resumen por entrenador ordenada por puntos medios."""
    require_columns(
        kpis,
        {
            "año",
            "entrenador",
            "pts_utd",
            "pos_utd",
            "gf_utd",
            "ppg",
            "pts_por_gol",
            "brecha_puntos",
        },
        "manager_summary",
    )
    return (
        kpis.groupby("entrenador")
        .agg(
            temporadas=("año", "count"),
            pts_promedio=("pts_utd", "mean"),
            posicion_media=("pos_utd", "mean"),
            goles_promedio=("gf_utd", "mean"),
            ppg=("ppg", "mean"),
            eficiencia=("pts_por_gol", "mean"),
            brecha_vs_campeon=("brecha_puntos", "mean"),
        )
        .round(2)
        .sort_values("pts_promedio", ascending=False)
    )


# ── Benchmark frente a la liga ────────────────────────────────────────────────


def _league_period(pl_tables: pd.DataFrame) -> pd.DataFrame:
    df = pl_tables[pl_tables["season_end_year"].isin(SEASONS)].copy()
    df["ppg"] = safe_divide(df["points"], df["played"])
    return df


def league_benchmark(pl_tables: pd.DataFrame) -> pd.DataFrame:
    """PPG del United frente a la media de la Premier League sin el United.

    Returns
    -------
    pd.DataFrame
        Columnas ``temporada``, ``united_pts``, ``united_ppg``,
        ``pl_avg_pts_sin_utd``, ``pl_avg_ppg_sin_utd``, ``diff_ppg_vs_pl``.
    """
    df = _league_period(pl_tables)
    is_utd = df["team"] == TEAM_NAME
    utd = df[is_utd].set_index("season_end_year")
    rest = df[~is_utd].groupby("season_end_year")[["points", "ppg"]].mean()
    bench = pd.DataFrame(
        {
            "temporada": utd.index.astype(int),
            "united_pts": utd["points"].astype(int).to_numpy(),
            "united_ppg": utd["ppg"].round(3).to_numpy(),
            "pl_avg_pts_sin_utd": rest.loc[utd.index, "points"].round(1).to_numpy(),
            "pl_avg_ppg_sin_utd": rest.loc[utd.index, "ppg"].round(3).to_numpy(),
            "diff_ppg_vs_pl": (utd["ppg"] - rest.loc[utd.index, "ppg"]).round(3).to_numpy(),
        }
    )
    return bench.sort_values("temporada").reset_index(drop=True)


def group_benchmark(pl_tables: pd.DataFrame) -> pd.DataFrame:
    """PPG medio del período para United, resto del Top 6 y resto de la liga."""
    df = _league_period(pl_tables)
    group = np.select(
        [df["team"] == TEAM_NAME, df["team"].isin(TOP_SIX)],
        [TEAM_NAME, "Top 6 (sin Utd)"],
        default="Resto PL",
    )
    return (
        df.assign(Grupo=group)
        .groupby("Grupo")["ppg"]
        .mean()
        .round(3)
        .rename("PPG_Promedio")
        .reset_index()
        .sort_values("PPG_Promedio", ascending=False)
        .reset_index(drop=True)
    )


# ── Pases por 90 minutos ──────────────────────────────────────────────────────


def passing_per_90(passing: pd.DataFrame, min_minutes: int = MIN_MINUTES_PASSING) -> pd.DataFrame:
    """Pases progresivos (PrgP/90) y pases clave (KP/90) con percentil de plantel.

    Parameters
    ----------
    passing : pd.DataFrame
        Exportación FBref saneada por :func:`manutd_analysis.data_loader.load_passing`.
    min_minutes : int
        Minutos mínimos jugados (la columna FBref ``90s`` se compara con
        ``min_minutes / 90``).

    Returns
    -------
    pd.DataFrame
        Columnas ``jugador``, ``pos``, ``min_90s``, ``prgp``, ``kp``,
        ``prgp_90``, ``kp_90``, ``pct_prgp_plantel``, ``pct_kp_plantel``,
        ordenadas por ``prgp_90``. Los percentiles son internos del plantel.
    """
    require_columns(passing, {"Player", "Pos", "90s", "KP", "PrgP"}, "passing_per_90")
    df = passing[passing["90s"] >= min_minutes / 90].copy()
    df["prgp_90"] = safe_divide(df["PrgP"], df["90s"]).round(2)
    df["kp_90"] = safe_divide(df["KP"], df["90s"]).round(2)
    df["pct_prgp_plantel"] = (df["prgp_90"].rank(pct=True) * 100).round(0).astype(int)
    df["pct_kp_plantel"] = (df["kp_90"].rank(pct=True) * 100).round(0).astype(int)
    return (
        df[
            [
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
        ]
        .rename(
            columns={
                "Player": "jugador",
                "Pos": "pos",
                "90s": "min_90s",
                "PrgP": "prgp",
                "KP": "kp",
            }
        )
        .sort_values("prgp_90", ascending=False)
        .reset_index(drop=True)
    )


# ── Hallazgos clave ───────────────────────────────────────────────────────────


def key_findings(kpis: pd.DataFrame, benchmark: pd.DataFrame | None = None) -> dict:
    """Resume los hallazgos cuantitativos que se publican en README y dashboard.

    Parameters
    ----------
    kpis : pd.DataFrame
        Tabla de :func:`build_season_kpis`.
    benchmark : pd.DataFrame | None
        Salida de :func:`league_benchmark`; si se entrega, agrega la ventaja
        media de PPG frente al resto de la liga.

    Returns
    -------
    dict
        Diccionario serializable a JSON.
    """
    per_manager = ppg_by_manager(kpis, exclude_transitions=True)
    comparison = stability_comparison(kpis)
    champion_ppg = safe_divide(kpis["pts_champ"], kpis["played"])
    findings: dict = {
        "rango": f"{int(kpis['año'].min())}-{int(kpis['año'].max())}",
        "n_temporadas": int(len(kpis)),
        "n_entrenadores": int(kpis.loc[~kpis["es_transicion"], "entrenador"].nunique()),
        "n_temporadas_transicion": int(kpis["es_transicion"].sum()),
        "brecha_media": round(float(kpis["brecha_puntos"].mean()), 1),
        "brecha_min": int(kpis["brecha_puntos"].min()),
        "brecha_max": int(kpis["brecha_puntos"].max()),
        "pts_promedio": round(float(kpis["pts_utd"].mean()), 1),
        "ppg_promedio": round(float(kpis["ppg"].mean()), 3),
        "ppg_campeon_promedio": round(float(champion_ppg.mean()), 3),
        "pos_media": round(float(kpis["pos_utd"].mean()), 1),
        "temporadas_top4": int((kpis["pos_utd"] <= 4).sum()),
        "mejor_dt": {"nombre": str(per_manager.idxmax()), "ppg": float(per_manager.max())},
        "peor_dt": {"nombre": str(per_manager.idxmin()), "ppg": float(per_manager.min())},
        "costo_inestabilidad": round(instability_cost(comparison), 1),
    }
    if benchmark is not None and not benchmark.empty:
        findings["ventaja_ppg_vs_pl"] = round(float(benchmark["diff_ppg_vs_pl"].mean()), 3)
    return findings
