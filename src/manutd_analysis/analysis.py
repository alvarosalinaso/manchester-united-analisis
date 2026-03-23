import pandas as pd

def get_efficiency_df(d_f: pd.DataFrame) -> pd.Series:
    _check_cols(d_f, {"entrenador", "pts_por_gol"})
    return d_f.groupby("entrenador")["pts_por_gol"].mean().sort_values(ascending=False).round(3)

def get_stability_df(d_f: pd.DataFrame) -> pd.DataFrame:
    _check_cols(d_f, {"entrenador", "pts_utd", "brecha_puntos", "gf_utd"})
    t = d_f.copy()
    t["is_transition"] = t["entrenador"].astype(str).str.contains("/", regex=False)
    comp = (
        t.groupby("is_transition")[["pts_utd", "brecha_puntos", "gf_utd", "ppg"]]
        .mean()
        .round(2)
    )
    comp.index = ["Estable (1 DT)", "Caos (Transición)"]
    return comp

def calc_instability_cost(comp: pd.DataFrame) -> float:
    try:
        return float(comp.loc["Estable (1 DT)", "pts_utd"] - comp.loc["Caos (Transición)", "pts_utd"])
    except KeyError:
        return 0.0

def aggregate_manager_stats(d_f: pd.DataFrame) -> pd.DataFrame:
    _check_cols(d_f, {"entrenador", "pts_utd", "gf_utd", "ppg", "pts_por_gol", "brecha_puntos"})
    return (
        d_f.groupby("entrenador")
        .agg(
            temporadas=("año", "count"),
            pts_promedio=("pts_utd", "mean"),
            goles_promedio=("gf_utd", "mean"),
            ppg=("ppg", "mean"),
            eficiencia=("pts_por_gol", "mean"),
            brecha_vs_campeon=("brecha_puntos", "mean"),
        )
        .round(2)
        .sort_values("pts_promedio", ascending=False)
    )

def _check_cols(d_f: pd.DataFrame, req: set) -> None:
    miss = req - set(d_f.columns)
    if miss: raise ValueError(f"Faltan columnas: {miss}")
