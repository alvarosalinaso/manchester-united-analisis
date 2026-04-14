import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Manchester United | Auditoría de Rendimiento",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.main { background-color: #0a0a0f; }
.block-container { padding-top: 1.5rem; }
h1, h2, h3 { font-family: 'Bebas Neue', sans-serif; letter-spacing: 2px; color: #DA291C; }
.metric-card {
    background: #12121a;
    border: 1px solid #1e1e2e;
    border-left: 3px solid #DA291C;
    border-radius: 8px;
    padding: 1rem 1.2rem;
}
.metric-val { font-size: 2rem; font-weight: 500; color: #f0f0f0; }
.metric-lab { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }
.stSelectbox label, .stSlider label, .stMultiSelect label { color: #ccc; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ── DATOS ──────────────────────────────────────────────────────────────────────
np.random.seed(42)

ENTRENADORES = {
    range(2014, 2015): "David Moyes",
    range(2015, 2017): "Louis van Gaal",
    range(2017, 2019): "José Mourinho",
    range(2019, 2022): "Ole Gunnar Solskjær",
    range(2022, 2023): "Erik ten Hag (1a)",
    range(2023, 2025): "Erik ten Hag (2a)",
}

def get_manager(year):
    for r, m in ENTRENADORES.items():
        if year in r:
            return m
    return "Desconocido"

# Generar datos de temporadas
seasons = []
for yr in range(2014, 2025):
    mgr = get_manager(yr)
    base_pts = {"David Moyes": 64, "Louis van Gaal": 70, "José Mourinho": 69,
                "Ole Gunnar Solskjær": 66, "Erik ten Hag (1a)": 58, "Erik ten Hag (2a)": 44}
    pts = base_pts.get(mgr, 60) + np.random.randint(-5, 6)
    gf = int(pts * 0.82 + np.random.randint(-5, 6))
    ga = int(80 - pts * 0.55 + np.random.randint(-4, 5))
    xg = round(pts * 0.032 + np.random.uniform(-0.2, 0.2), 2)
    xga = round(2.5 - pts * 0.02 + np.random.uniform(-0.1, 0.1), 2)
    seasons.append({
        "season": f"{yr}/{str(yr+1)[-2:]}",
        "year": yr,
        "manager": mgr,
        "points": pts,
        "goals_for": gf,
        "goals_against": ga,
        "xg": xg,
        "xga": xga,
        "gd": gf - ga,
        "position": max(1, min(20, int(20 - pts / 5 + np.random.randint(-1, 2)))),
        "wins": int(pts / 3 * 0.75),
        "draws": int(pts / 3 * 0.25),
        "losses": int(38 - pts / 3),
    })

df_seasons = pd.DataFrame(seasons)

# Datos de jugadores 2024/25
players_data = [
    {"player": "B. Fernandes", "pos": "CAM", "apps": 32, "goals": 8, "assists": 10,
     "pass_acc": 88.4, "prog_passes": 5.1, "xg": 7.8, "xa": 8.2, "duels_won": 47.0,
     "distance_km": 10.8, "market_value": 70},
    {"player": "R. Højlund", "pos": "ST", "apps": 20, "goals": 7, "assists": 2,
     "pass_acc": 83.1, "prog_passes": 2.1, "xg": 8.9, "xa": 2.0, "duels_won": 48.0,
     "distance_km": 9.2, "market_value": 70},
    {"player": "K. Mainoo", "pos": "CM", "apps": 28, "goals": 2, "assists": 3,
     "pass_acc": 85.7, "prog_passes": 4.0, "xg": 1.8, "xa": 3.2, "duels_won": 58.4,
     "distance_km": 11.1, "market_value": 60},
    {"player": "A. Garnacho", "pos": "RW", "apps": 34, "goals": 7, "assists": 6,
     "pass_acc": 74.1, "prog_passes": 1.8, "xg": 6.1, "xa": 4.5, "duels_won": 43.5,
     "distance_km": 10.5, "market_value": 55},
    {"player": "M. Ugarte", "pos": "CDM", "apps": 22, "goals": 0, "assists": 1,
     "pass_acc": 89.1, "prog_passes": 3.4, "xg": 0.4, "xa": 0.8, "duels_won": 65.2,
     "distance_km": 11.5, "market_value": 50},
    {"player": "L. Martínez", "pos": "CB", "apps": 29, "goals": 1, "assists": 1,
     "pass_acc": 93.4, "prog_passes": 6.5, "xg": 0.9, "xa": 0.5, "duels_won": 66.4,
     "distance_km": 9.8, "market_value": 60},
    {"player": "D. Dalot", "pos": "RB", "apps": 35, "goals": 2, "assists": 4,
     "pass_acc": 84.1, "prog_passes": 4.2, "xg": 1.5, "xa": 2.5, "duels_won": 55.2,
     "distance_km": 11.2, "market_value": 35},
    {"player": "A. Onana", "pos": "GK", "apps": 36, "goals": 0, "assists": 0,
     "pass_acc": 72.4, "prog_passes": 4.5, "xg": 0.0, "xa": 0.0, "duels_won": 80.0,
     "distance_km": 5.5, "market_value": 45},
    {"player": "Casemiro", "pos": "CDM", "apps": 26, "goals": 1, "assists": 1,
     "pass_acc": 86.5, "prog_passes": 3.2, "xg": 0.8, "xa": 1.5, "duels_won": 59.8,
     "distance_km": 10.1, "market_value": 15},
    {"player": "A. Diallo", "pos": "LW", "apps": 22, "goals": 5, "assists": 3,
     "pass_acc": 81.2, "prog_passes": 2.5, "xg": 4.2, "xa": 3.1, "duels_won": 45.1,
     "distance_km": 10.3, "market_value": 40},
    {"player": "M. de Ligt", "pos": "CB", "apps": 26, "goals": 1, "assists": 0,
     "pass_acc": 91.0, "prog_passes": 3.8, "xg": 0.7, "xa": 0.2, "duels_won": 71.0,
     "distance_km": 9.6, "market_value": 38},
    {"player": "C. Eriksen", "pos": "CM", "apps": 24, "goals": 1, "assists": 4,
     "pass_acc": 91.2, "prog_passes": 4.8, "xg": 1.0, "xa": 4.1, "duels_won": 42.1,
     "distance_km": 10.2, "market_value": 12},
]
df_players = pd.DataFrame(players_data)

# Datos de partidos jornada a jornada 2024/25
np.random.seed(7)
matchdays = []
pts_acc = 0
for md in range(1, 39):
    result = np.random.choice(["W", "D", "L"], p=[0.38, 0.22, 0.40])
    gf = np.random.poisson(1.3) if result != "L" else np.random.poisson(0.8)
    ga = np.random.poisson(0.8) if result == "W" else np.random.poisson(1.5)
    if result == "W": pts = 3
    elif result == "D": pts = 1
    else: pts = 0
    pts_acc += pts
    matchdays.append({
        "matchday": md, "result": result, "gf": gf, "ga": ga,
        "pts": pts, "pts_acc": pts_acc,
        "xg": round(np.random.uniform(0.8, 2.4), 2),
        "xga": round(np.random.uniform(0.6, 2.2), 2),
    })
df_matches = pd.DataFrame(matchdays)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚽ Filtros")
    st.markdown("---")

    vista = st.selectbox("Vista principal", [
        "Evolución histórica", "Rendimiento 24/25", "Análisis de jugadores", "Comparativa de métricas"
    ])

    if vista == "Evolución histórica":
        managers_sel = st.multiselect("Entrenadores",
            options=df_seasons["manager"].unique().tolist(),
            default=df_seasons["manager"].unique().tolist())
        metrica_hist = st.selectbox("Métrica", ["points", "goals_for", "goals_against", "xg", "xga", "gd", "position"])
        year_range = st.slider("Temporadas", 2014, 2024, (2014, 2024))

    elif vista == "Análisis de jugadores":
        pos_sel = st.multiselect("Posición", options=df_players["pos"].unique().tolist(),
            default=df_players["pos"].unique().tolist())
        eje_x = st.selectbox("Eje X", ["pass_acc", "prog_passes", "xg", "xa", "duels_won", "distance_km", "market_value"])
        eje_y = st.selectbox("Eje Y", ["goals", "assists", "xg", "xa", "pass_acc", "duels_won"])
        color_by = st.selectbox("Color por", ["pos", "market_value", "apps"])

    elif vista == "Comparativa de métricas":
        players_sel = st.multiselect("Jugadores (máx 5)",
            options=df_players["player"].tolist(),
            default=["B. Fernandes", "K. Mainoo", "M. Ugarte", "R. Højlund", "L. Martínez"])
        metricas_radar = st.multiselect("Métricas radar",
            options=["pass_acc", "prog_passes", "xg", "xa", "duels_won", "goals", "assists"],
            default=["pass_acc", "prog_passes", "xg", "xa", "duels_won"])

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#666; line-height:1.6'>
    Álvaro Salinas Ortiz<br>
    <a href='https://github.com/alvarosalinaso' style='color:#DA291C'>github.com/alvarosalinaso</a>
    </div>
    """, unsafe_allow_html=True)

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("# MANCHESTER UNITED")
st.markdown(f"### {vista.upper()}")
st.markdown("---")

# ── VISTAS ─────────────────────────────────────────────────────────────────────

if vista == "Evolución histórica":
    df_f = df_seasons[
        (df_seasons["manager"].isin(managers_sel)) &
        (df_seasons["year"] >= year_range[0]) &
        (df_seasons["year"] <= year_range[1])
    ]

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='metric-card'><div class='metric-val'>{df_f['points'].mean():.0f}</div><div class='metric-lab'>Pts promedio/temporada</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><div class='metric-val'>{df_f['goals_for'].sum()}</div><div class='metric-lab'>Goles totales</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'><div class='metric-val'>{df_f['position'].min()}°</div><div class='metric-lab'>Mejor posición</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='metric-card'><div class='metric-val'>{df_f['position'].max()}°</div><div class='metric-lab'>Peor posición</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    labels = {"points": "Puntos", "goals_for": "Goles a favor", "goals_against": "Goles en contra",
               "xg": "xG por partido", "xga": "xGA por partido", "gd": "Diferencia de goles", "position": "Posición"}

    fig = px.line(df_f, x="season", y=metrica_hist, color="manager",
                  markers=True, title=f"{labels[metrica_hist]} por temporada",
                  color_discrete_sequence=["#DA291C", "#FBE122", "#ffffff", "#888", "#4CAF50", "#2196F3"])
    fig.update_layout(template="plotly_dark", plot_bgcolor="#12121a", paper_bgcolor="#0a0a0f",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02),
                      height=380, font=dict(family="DM Sans"))
    if metrica_hist == "position":
        fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Goles a favor", x=df_f["season"], y=df_f["goals_for"], marker_color="#DA291C"))
        fig2.add_trace(go.Bar(name="Goles en contra", x=df_f["season"], y=df_f["goals_against"], marker_color="#444"))
        fig2.update_layout(barmode="group", template="plotly_dark", plot_bgcolor="#12121a",
                           paper_bgcolor="#0a0a0f", height=300, title="Goles por temporada",
                           font=dict(family="DM Sans"))
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        fig3 = px.scatter(df_f, x="xg", y="goals_for", color="manager", size="points",
                          hover_data=["season", "manager", "points"],
                          title="xG vs Goles reales",
                          color_discrete_sequence=["#DA291C", "#FBE122", "#fff", "#888", "#4CAF50", "#2196F3"])
        fig3.add_shape(type="line", x0=df_f["xg"].min(), y0=df_f["xg"].min()*28,
                       x1=df_f["xg"].max(), y1=df_f["xg"].max()*28,
                       line=dict(color="#666", dash="dash"))
        fig3.update_layout(template="plotly_dark", plot_bgcolor="#12121a",
                           paper_bgcolor="#0a0a0f", height=300, font=dict(family="DM Sans"))
        st.plotly_chart(fig3, use_container_width=True)

elif vista == "Rendimiento 24/25":
    # KPIs jornada actual
    last = df_matches.iloc[-1]
    wins = len(df_matches[df_matches["result"] == "W"])
    draws = len(df_matches[df_matches["result"] == "D"])
    losses = len(df_matches[df_matches["result"] == "L"])

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, val, lab in zip([c1,c2,c3,c4,c5],
        [last["pts_acc"], wins, draws, losses, f"{df_matches['xg'].mean():.2f}"],
        ["Puntos totales", "Victorias", "Empates", "Derrotas", "xG promedio"]):
        col.markdown(f"<div class='metric-card'><div class='metric-val'>{val}</div><div class='metric-lab'>{lab}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Acumulado de puntos
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_matches["matchday"], y=df_matches["pts_acc"],
                             mode="lines+markers", name="Puntos acumulados",
                             line=dict(color="#DA291C", width=3),
                             marker=dict(size=6, color=[
                                 "#DA291C" if r == "W" else "#FBE122" if r == "D" else "#444"
                                 for r in df_matches["result"]])))
    # Línea de referencia Champions
    fig.add_hline(y=72, line_dash="dash", line_color="#4CAF50", annotation_text="Top 4 ref (~72 pts)")
    fig.update_layout(template="plotly_dark", plot_bgcolor="#12121a", paper_bgcolor="#0a0a0f",
                      title="Acumulado de puntos — Jornada a jornada",
                      xaxis_title="Jornada", yaxis_title="Puntos",
                      height=350, font=dict(family="DM Sans"))
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        # xG vs xGA por jornada
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_matches["matchday"], y=df_matches["xg"],
                              name="xG (ataque)", marker_color="#DA291C", opacity=0.85))
        fig2.add_trace(go.Bar(x=df_matches["matchday"], y=-df_matches["xga"],
                              name="xGA (defensa)", marker_color="#444", opacity=0.85))
        fig2.update_layout(barmode="overlay", template="plotly_dark",
                           plot_bgcolor="#12121a", paper_bgcolor="#0a0a0f",
                           title="xG ofensivo vs defensivo por jornada",
                           height=310, font=dict(family="DM Sans"))
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        # Distribución de resultados
        results_count = df_matches["result"].value_counts()
        fig3 = go.Figure(go.Pie(
            labels=["Victorias", "Empates", "Derrotas"],
            values=[wins, draws, losses],
            hole=0.55,
            marker_colors=["#DA291C", "#FBE122", "#2a2a3a"],
            textfont_size=13))
        fig3.update_layout(template="plotly_dark", paper_bgcolor="#0a0a0f",
                           title="Distribución de resultados",
                           height=310, font=dict(family="DM Sans"))
        st.plotly_chart(fig3, use_container_width=True)

elif vista == "Análisis de jugadores":
    df_p = df_players[df_players["pos"].isin(pos_sel)]

    labels_map = {
        "pass_acc": "Precisión de pase %", "prog_passes": "Pases progresivos/90",
        "xg": "xG total", "xa": "xA total", "duels_won": "Duelos ganados %",
        "distance_km": "Distancia km/90", "market_value": "Valor mercado (M€)",
        "goals": "Goles", "assists": "Asistencias", "apps": "Partidos"
    }

    fig = px.scatter(df_p, x=eje_x, y=eje_y, color=color_by,
                     size="apps", text="player", hover_data=["pos", "apps", "market_value"],
                     title=f"{labels_map.get(eje_x, eje_x)} vs {labels_map.get(eje_y, eje_y)}",
                     color_discrete_sequence=px.colors.qualitative.Bold if color_by == "pos" else None,
                     color_continuous_scale="Reds" if color_by != "pos" else None)
    fig.update_traces(textposition="top center", marker=dict(line=dict(width=1, color="white")))
    fig.update_layout(template="plotly_dark", plot_bgcolor="#12121a", paper_bgcolor="#0a0a0f",
                      height=480, font=dict(family="DM Sans"))
    st.plotly_chart(fig, use_container_width=True)

    # Tabla resumen
    cols_show = ["player", "pos", "apps", "goals", "assists", "pass_acc", "xg", "xa", "duels_won", "market_value"]
    st.dataframe(
        df_p[cols_show].sort_values("market_value", ascending=False).reset_index(drop=True)
        .rename(columns={c: labels_map.get(c, c) for c in cols_show}),
        use_container_width=True, height=300
    )

elif vista == "Comparativa de métricas":
    players_sel = players_sel[:5]
    df_r = df_players[df_players["player"].isin(players_sel)].set_index("player")

    if len(metricas_radar) < 3:
        st.warning("Selecciona al menos 3 métricas para el radar.")
    else:
        # Normalizar 0-1
        df_norm = df_r[metricas_radar].copy()
        for col in metricas_radar:
            rng = df_norm[col].max() - df_norm[col].min()
            df_norm[col] = (df_norm[col] - df_norm[col].min()) / (rng if rng > 0 else 1)

        colors = ["#DA291C", "#FBE122", "#4CAF50", "#2196F3", "#FF9800"]
        fig = go.Figure()
        for i, player in enumerate(players_sel):
            if player not in df_norm.index:
                continue
            vals = df_norm.loc[player, metricas_radar].tolist()
            vals += [vals[0]]
            labels_r = metricas_radar + [metricas_radar[0]]
            fig.add_trace(go.Scatterpolar(
                r=vals, theta=labels_r, name=player,
                line=dict(color=colors[i % len(colors)], width=2),
                fill="toself", fillcolor=colors[i % len(colors)],
                opacity=0.18
            ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=9)),
                       bgcolor="#12121a"),
            template="plotly_dark", paper_bgcolor="#0a0a0f",
            title="Radar comparativo de jugadores",
            height=520, font=dict(family="DM Sans"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabla de valores reales
        st.markdown("#### Valores reales")
        label_map = {"pass_acc": "Prec. pase %", "prog_passes": "Pas. prog.", "xg": "xG",
                     "xa": "xA", "duels_won": "Duelos %", "goals": "Goles", "assists": "Asist."}
        display_cols = {m: label_map.get(m, m) for m in metricas_radar}
        st.dataframe(
            df_r.loc[[p for p in players_sel if p in df_r.index], metricas_radar]
            .rename(columns=display_cols).round(2),
            use_container_width=True
        )
