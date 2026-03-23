import pandas as pd
import streamlit as st

@st.cache_data
def cargar_datos_streamlit() -> pd.DataFrame:
    """Carga los datos preprocesados para el dashboard y genera KPIs."""
    df = pd.read_csv("data/raw/streamlit_data.csv")
    df["ppg"]     = (df["points"] / df["games"]).round(3)
    df["gap"]     = df["champ_pts"] - df["points"]
    df["gd"]      = df["gf"] - df["ga"]
    df["win_pct"] = (df["wins"] / df["games"] * 100).round(1)
    
    # Forzar el parseo booleano
    df["manager_fired"] = df["manager_fired"].astype(str).str.lower().map({'true': True, 'false': False})
    
    return df

@st.cache_data
def kpi_globales(df: pd.DataFrame) -> dict:
    """Retorna los KPIs principales."""
    return {
        "n_seasons": len(df),
        "total_gap": df["gap"].sum(),
        "avg_ppg": df["ppg"].mean(),
        "total_comp": df["comp_fee_m"].sum(),
        "total_net_spend": df["net_spend_m"].sum(),
        "titles": 0,  # 2014-2024
        "avg_pos": df["position"].mean()
    }

@st.cache_data
def agrupar_por_entrenador(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega las estadísticas por entrenador para comparativas."""
    grp = df.groupby("manager_clean").agg(
        seasons=("season", "count"),
        pts_total=("points", "sum"),
        ppg=("ppg", "mean"),
        avg_pos=("position", "mean"),
        avg_gf=("gf", "mean"),
        avg_ga=("ga", "mean"),
        total_comp=("comp_fee_m", "sum"),
        total_net_spend=("net_spend_m", "sum")
    ).reset_index()
    
    grp["ppg"] = grp["ppg"].round(3)
    grp["avg_pos"] = grp["avg_pos"].round(1)
    grp["cost_per_point"] = (grp["total_net_spend"] / grp["pts_total"]).round(2)
    return grp.sort_values("ppg", ascending=False)
