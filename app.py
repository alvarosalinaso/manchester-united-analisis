"""
═══════════════════════════════════════════════════════════════════════════════
  Manchester United Performance Analysis — Streamlit App
  Autor : Álvaro Salinas Ortiz  |  github.com/alvarosalinaso
  Stack : Streamlit · Plotly · Pandas · SciPy · Scikit-learn
═══════════════════════════════════════════════════════════════════════════════

PROBLEMA DE NEGOCIO
-------------------
  La inestabilidad táctica en el banquillo tiene un costo medible en:
  (1) Puntos perdidos en la tabla, (2) Gasto en indemnizaciones (~£200M en
  10 años) y (3) Devaluación del plantel. Este dashboard provee a directivos
  deportivos un modelo de benchmarking de rendimiento que les permite:
  — Comparar objetivamente gestiones técnicas
  — Identificar temporadas de quiebre sistémico
  — Estimar el impacto esperado de un nuevo entrenador
  Es una herramienta de decisión, no un análisis histórico pasivo.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import warnings

warnings.filterwarnings("ignore")

# ─────────────────────────────── CONFIG ───────────────────────────────
st.set_page_config(
    page_title="Man Utd Performance Intelligence | alvarosalinaso",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLORS = {
    "manutd":   "#DA291C",
    "champ":    "#3fb950",
    "accent":   "#58a6ff",
    "warn":     "#e3b341",
    "bad":      "#f78166",
    "bg":       "#0d1117",
    "card":     "#161b22",
    "border":   "#30363d",
    "text":     "#e6edf3",
    "text2":    "#8b949e",
}

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(22,27,34,0.6)",
    font=dict(family="Inter, sans-serif", color=COLORS["text"], size=12),
    margin=dict(l=10, r=10, t=45, b=10),
    xaxis=dict(gridcolor="#30363d", zerolinecolor="#30363d"),
    yaxis=dict(gridcolor="#30363d", zerolinecolor="#30363d"),
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.block-container{padding:1.5rem 2rem;}
.stApp{background-color:#0d1117;color:#e6edf3;}
[data-testid="stSidebar"]{background:#161b22!important;border-right:1px solid #30363d;}
[data-testid="metric-container"]{background:#161b22!important;border:1px solid #30363d;border-radius:12px;padding:.8rem 1rem;}
[data-testid="stMetricValue"]{color:#DA291C!important;font-weight:800!important;}
h1{color:#DA291C!important;font-weight:800!important;letter-spacing:-1px;}
h2,h3{color:#e6edf3!important;font-weight:700!important;}
button[data-baseweb="tab"][aria-selected="true"]{color:#DA291C!important;border-bottom-color:#DA291C!important;}
[data-baseweb="select"]>div{background-color:#21262d!important;border-color:#30363d!important;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────── DATA LAYER ───────────────────────────
@st.cache_data
def load_data():
    seasons = [
        "2013-14","2014-15","2015-16","2016-17","2017-18",
        "2018-19","2019-20","2020-21","2021-22","2022-23","2023-24",
    ]
    data = {
        "season":       seasons,
        "manager":      ["Moyes","Van Gaal","Van Gaal","Mourinho","Mourinho",
                         "Solskjær","Solskjær","Solskjær","Rangnick/Ten Hag","Ten Hag","Ten Hag"],
        "manager_clean":["D. Moyes","L. Van Gaal","L. Van Gaal","J. Mourinho","J. Mourinho",
                         "O. Solskjær","O. Solskjær","O. Solskjær","Mixed","E. Ten Hag","E. Ten Hag"],
        "points":       [64, 70, 66, 69, 81, 66, 66, 74, 58, 75, 60],
        "champ_pts":    [86, 87, 78, 93, 100, 98, 81, 86, 93, 89, 89],
        "position":     [7,  4,  5,  6,  2,  6,  3,  2,  6,  3,  8],
        "gf":           [64, 62, 49, 54, 68, 65, 66, 73, 57, 58, 42],
        "ga":           [43, 37, 35, 35, 28, 54, 36, 44, 57, 43, 66],
        "wins":         [19, 20, 19, 18, 25, 19, 18, 21, 16, 23, 15],
        "draws":        [7,  10, 9,  15, 6,  9,  12, 11, 10, 6,  7],
        "losses":       [12, 8,  10, 5,  7,  10, 8,  6,  12, 9,  16],
        "games":        [38] * 11,
        "manager_fired":[True, False, False, True, False, True, False, False, True, False, False],
        "ucl_exits":    ["GS","R16","R16","SF","R16","R16","QF","R16","GS","R16","GS"],
        # Costo real estimado de saneamiento (£M) — dato investigado
        "comp_fee_m":   [5, 0, 0, 19.6, 0, 7.5, 0, 0, 0, 0, 0],
    }
    df = pd.DataFrame(data)
    df["ppg"]     = (df["points"] / df["games"]).round(3)
    df["gap"]     = df["champ_pts"] - df["points"]
    df["gd"]      = df["gf"] - df["ga"]
    df["win_pct"] = (df["wins"] / df["games"] * 100).round(1)
    return df


df = load_data()

# Datos de manager consolidados
@st.cache_data
def manager_summary(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby("manager_clean").agg(
        seasons=("season", "count"),
        pts_total=("points", "sum"),
        ppg=("ppg", "mean"),
        avg_pos=("position", "mean"),
        avg_gf=("gf", "mean"),
        avg_ga=("ga", "mean"),
        total_comp=("comp_fee_m", "sum"),
    ).reset_index()
    grp["ppg"] = grp["ppg"].round(3)
    grp["avg_pos"] = grp["avg_pos"].round(1)
    grp = grp.sort_values("ppg", ascending=False)
    return grp


mgr_df = manager_summary(df)


# ─────────────────────────────── SIDEBAR ──────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;margin-bottom:1rem;'>
      <div style='font-size:2rem;'>⚽</div>
      <div style='font-weight:800;font-size:1rem;color:#DA291C;'>Performance Intelligence</div>
      <div style='font-size:.75rem;color:#8b949e;'>Manchester United · 2013-2024</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    sel_seasons = st.multiselect(
        "Temporadas", df["season"].tolist(),
        default=df["season"].tolist(), key="seasons_sel",
    )
    sel_managers = st.multiselect(
        "Entrenadores", df["manager_clean"].unique().tolist(),
        default=df["manager_clean"].unique().tolist(), key="mgr_sel",
    )

    st.markdown("---")
    benchmark_mode = st.toggle("📌 Modo comparativa vs PL Top 6", value=True)
    show_trend     = st.toggle("📈 Mostrar línea de tendencia", value=True)

    st.markdown("---")
    st.markdown(
        "<div style='font-size:.75rem;color:#8b949e;'>🔗 <a href='https://github.com/alvarosalinaso/manchester-united-analisis' style='color:#58a6ff;'>Ver en GitHub</a></div>",
        unsafe_allow_html=True,
    )


df_f = df[df["season"].isin(sel_seasons) & df["manager_clean"].isin(sel_managers)]


# ─────────────────────────────── HEADER ───────────────────────────────
st.markdown("""
<h1 style='margin-bottom:0;'>⚽ Manchester United · Performance Intelligence</h1>
<p style='color:#8b949e;margin-top:.2rem;'>
  Benchmarking directivo · Premier League 2013-2024 · Herramienta de decisión deportiva
</p>
""", unsafe_allow_html=True)
st.markdown("---")


# ─────────────────────────────── KPI ROW ──────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)
total_gap   = df_f["gap"].sum()
total_comp  = df["comp_fee_m"].sum()
avg_ppg     = df_f["ppg"].mean()
best_ppg    = mgr_df["ppg"].max()
avg_gap     = df_f["gap"].mean()
titles      = 1

with k1: st.metric("Temporadas analizadas", len(df_f))
with k2: st.metric("Puntos perdidos vs campeón", f"{total_gap}", delta=f"{avg_gap:.0f} pts/temporada", delta_color="inverse")
with k3: st.metric("PPG promedio", f"{avg_ppg:.2f}", delta=f"vs {best_ppg:.2f} (Mourinho)")
with k4: st.metric("Coste indemnizaciones", f"£{total_comp:.1f}M", delta="10 años", delta_color="off")
with k5: st.metric("Títulos Premier", titles, delta="-9 vs Top6 líderes", delta_color="inverse")
with k6: st.metric("Posición promedio PL", f"{df_f['position'].mean():.1f}°")

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────── TABS ─────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Rendimiento Histórico",
    "👔 Análisis por Entrenador",
    "🔬 Diagnóstico Sistémico",
    "🔮 Proyección & Simulador",
])


# ══════════════════════ TAB 1: HISTÓRICO ══════════════════════
with tab1:
    # Chart 1: Puntos con comparativa
    fig_pts = go.Figure()
    fig_pts.add_trace(go.Bar(
        x=df_f["season"], y=df_f["points"],
        name="Man Utd",
        marker=dict(
            color=df_f["points"],
            colorscale=[[0,"#f78166"],[0.5,"#e3b341"],[1,"#DA291C"]],
            showscale=False,
        ),
        text=df_f["points"], textposition="outside",
        textfont=dict(size=11, color="#e6edf3"),
        hovertemplate="<b>%{x}</b><br>Puntos: %{y}<br>DT: " +
                      df_f["manager_clean"].values[0] + "<extra></extra>",
    ))
    if benchmark_mode:
        fig_pts.add_trace(go.Scatter(
            x=df_f["season"], y=df_f["champ_pts"],
            mode="lines+markers", name="Campeón PL",
            line=dict(color=COLORS["champ"], width=2.5, dash="dash"),
            marker=dict(size=6),
            hovertemplate="<b>%{x}</b><br>Campeón: %{y} pts<extra></extra>",
        ))
        # Relleno brecha
        fig_pts.add_trace(go.Scatter(
            x=list(df_f["season"]) + list(df_f["season"])[::-1],
            y=list(df_f["champ_pts"]) + list(df_f["points"])[::-1],
            fill="toself", fillcolor="rgba(247,129,102,0.1)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Brecha con campeón", showlegend=True,
        ))

    if show_trend:
        x_num = list(range(len(df_f)))
        slope, intercept, *_ = stats.linregress(x_num, df_f["points"])
        trend_y = [slope * x + intercept for x in x_num]
        fig_pts.add_trace(go.Scatter(
            x=df_f["season"], y=trend_y,
            mode="lines", name=f"Tendencia ({slope:+.1f} pts/temporada)",
            line=dict(color=COLORS["accent"], width=1.5, dash="longdash"),
        ))

    # Marcadores de cambio de DT
    fired_df = df_f[df_f["manager_fired"]]
# --- CÓDIGO CORREGIDO PARA GRÁFICO DE PUNTOS ---
# Aseguramos que 'season' tenga formato válido y no haya nulos antes de graficar
df_events = df_events.dropna(subset=['season'])

for _, row in df_events.iterrows():
    # Validación estricta: Solo graficar si el valor es convertible a posición en el eje
    if row["season"] and str(row["season"]) != 'nan':
        try:
            fig_pts.add_vline(
                x=row["season"], 
                line_dash="dot", 
                line_color="#e3b341", 
                line_width=1.5,
                annotation_text=f"⚠️ {row.get('event_name', 'Evento')}", 
                annotation_position="top left",
                annotation_font_size=10,
                annotation_font_color="#e3b341"
            )
        except Exception as e:
            continue # Si un evento falla, no tumbamos todo el gráfico

    fig_pts.update_layout(
        **PLOTLY_THEME,
        title="Puntos por temporada — Manchester United vs Campeón de la Premier League",
        height=420, barmode="overlay",
        legend=dict(orientation="h", y=-0.15, x=0),
    )
    fig_pts.update_xaxes(tickangle=-25)
    st.plotly_chart(fig_pts, use_container_width=True)

    # Row 2
    col_a, col_b = st.columns(2)
    with col_a:
        fig_gd = go.Figure()
        fig_gd.add_trace(go.Bar(x=df_f["season"], y=df_f["gf"], name="Goles a favor",
                                 marker_color="rgba(63,185,80,0.7)", text=df_f["gf"], textposition="inside"))
        fig_gd.add_trace(go.Bar(x=df_f["season"], y=-df_f["ga"], name="Goles en contra",
                                 marker_color="rgba(247,129,102,0.7)", text=df_f["ga"], textposition="inside"))
        fig_gd.add_trace(go.Scatter(x=df_f["season"], y=df_f["gd"], mode="lines+markers",
                                     name="Diferencial", line=dict(color=COLORS["accent"], width=2.5),
                                     marker=dict(size=6)))
        fig_gd.update_layout(**PLOTLY_THEME, title="Goles: a favor / en contra / diferencial",
                               height=320, barmode="overlay")
        fig_gd.update_xaxes(tickangle=-25)
        st.plotly_chart(fig_gd, use_container_width=True)

    with col_b:
        fig_pos = go.Figure()
        colors_pos = [COLORS["manutd"] if p <= 4 else (COLORS["warn"] if p <= 6 else COLORS["bad"])
                      for p in df_f["position"]]
        fig_pos.add_trace(go.Bar(
            x=df_f["season"], y=df_f["position"],
            marker_color=colors_pos,
            text=df_f["position"].apply(lambda p: f"{p}°"),
            textposition="outside", textfont=dict(size=11),
        ))
        fig_pos.add_hline(y=4, line_dash="dash", line_color=COLORS["champ"],
                          annotation_text="Champions League zone", annotation_font_color=COLORS["champ"])
        fig_pos.update_layout(
            **PLOTLY_THEME, title="Posición final en Premier League",
            height=320, showlegend=False,
        )
        fig_pos.update_xaxes(tickangle=-25)
        fig_pos.update_yaxes(autorange="reversed", range=[0.5, 10.5])
        st.plotly_chart(fig_pos, use_container_width=True)


# ══════════════════════ TAB 2: ENTRENADORES ══════════════════════
with tab2:
    col_l, col_r = st.columns([3, 2])
    with col_l:
        fig_mgr = go.Figure()
        sorted_mgr = mgr_df.sort_values("ppg")
        bar_colors = [COLORS["manutd"] if ppg >= 1.8
                      else (COLORS["warn"] if ppg >= 1.6 else COLORS["bad"])
                      for ppg in sorted_mgr["ppg"]]
        fig_mgr.add_trace(go.Bar(
            y=sorted_mgr["manager_clean"], x=sorted_mgr["ppg"],
            orientation="h",
            marker=dict(color=bar_colors, opacity=0.85),
            text=sorted_mgr["ppg"].round(3),
            textposition="outside", textfont=dict(size=12),
        ))
        fig_mgr.add_vline(x=2.0, line_dash="dot", line_color=COLORS["champ"],
                          annotation_text="Elite (>2.0 ppg)", annotation_font_color=COLORS["champ"])
        fig_mgr.update_layout(
            **PLOTLY_THEME, title="Puntos por partido (PPG) — Comparativa de gestiones",
            height=360,
        )
        fig_mgr.update_xaxes(range=[0.8, 2.3])
        st.plotly_chart(fig_mgr, use_container_width=True)

    with col_r:
        # Scatter: PPG vs Goals For
        fig_scat = px.scatter(
            mgr_df, x="ppg", y="avg_gf",
            size="seasons", color="manager_clean",
            text="manager_clean",
            title="PPG vs Goles a favor (tamaño = temporadas)",
            color_discrete_sequence=px.colors.qualitative.Plotly,
            labels={"ppg": "PPG", "avg_gf": "Goles/temporada", "manager_clean": "DT"},
        )
        fig_scat.update_traces(textposition="top center", textfont_size=10)
        fig_scat.update_layout(**PLOTLY_THEME, height=360, showlegend=False)
        st.plotly_chart(fig_scat, use_container_width=True)

    # Tabla detallada
    st.markdown("#### 📋 Ficha comparativa de gestiones")
    display = mgr_df.rename(columns={
        "manager_clean": "Entrenador", "seasons": "Temporadas",
        "pts_total": "Pts totales", "ppg": "PPG",
        "avg_pos": "Pos. media", "avg_gf": "GF/temp.",
        "avg_ga": "GA/temp.", "total_comp": "Indemniz. (£M)",
    })
    st.dataframe(
        display.style
        .background_gradient(subset=["PPG"], cmap="RdYlGn", vmin=1.2, vmax=2.1)
        .background_gradient(subset=["Indemniz. (£M)"], cmap="Reds"),
        use_container_width=True, hide_index=True,
    )
    st.info("💡 **Hallazgo clave:** Los 4 cambios de entrenador en 10 años costaron £32.1M en indemnizaciones, más el costo oculto de ruptura táctica estimado en ~12 puntos de tabla (equivalente a ~£45M en diferencial de Champions League revenue).")


# ══════════════════════ TAB 3: DIAGNÓSTICO ══════════════════════
with tab3:
    st.markdown("#### 🔬 Análisis de correlaciones sistémicas")

    corr_vars = ["points", "gf", "ga", "gd", "wins", "position", "gap"]
    df_corr = df_f[corr_vars].corr()

    fig_corr = go.Figure(go.Heatmap(
        z=df_corr.values,
        x=df_corr.columns.tolist(),
        y=df_corr.columns.tolist(),
        colorscale=[[0,"#f78166"],[0.5,"#0d1117"],[1,"#3fb950"]],
        zmid=0, showscale=True,
        text=df_corr.values.round(2),
        texttemplate="%{text}",
        textfont=dict(size=11),
        colorbar=dict(bgcolor="rgba(0,0,0,0)", tickfont=dict(color="#8b949e")),
    ))
    fig_corr.update_layout(**PLOTLY_THEME, height=400,
                            title="Matriz de correlaciones — variables de rendimiento")
    st.plotly_chart(fig_corr, use_container_width=True)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        fig_wins = go.Figure()
        for col_w, name, color in [("wins","Victorias",COLORS["champ"]),
                                    ("draws","Empates",COLORS["warn"]),
                                    ("losses","Derrotas",COLORS["manutd"])]:
            fig_wins.add_trace(go.Bar(x=df_f["season"], y=df_f[col_w],
                                       name=name, marker_color=color, opacity=0.85))
        fig_wins.update_layout(**PLOTLY_THEME, barmode="stack",
                                title="Distribución de resultados por temporada",
                                height=320, legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_wins, use_container_width=True)

    with col_d2:
        # Regresión puntos ~ goles a favor
        x_reg = df_f["gf"].values
        y_reg = df_f["points"].values
        slope, intercept, r, p, _ = stats.linregress(x_reg, y_reg)
        x_line = np.linspace(x_reg.min() - 2, x_reg.max() + 2, 50)

        fig_reg = go.Figure()
        fig_reg.add_trace(go.Scatter(
            x=x_reg, y=y_reg, mode="markers",
            marker=dict(size=10, color=COLORS["manutd"], opacity=0.8),
            text=df_f["season"],
            hovertemplate="<b>%{text}</b><br>GF: %{x}<br>Pts: %{y}<extra></extra>",
            name="Temporadas",
        ))
        fig_reg.add_trace(go.Scatter(
            x=x_line, y=slope * x_line + intercept,
            mode="lines", line=dict(color=COLORS["accent"], width=2, dash="dash"),
            name=f"Regresión (R²={r**2:.2f})",
        ))
        fig_reg.update_layout(**PLOTLY_THEME,
                               title="Regresión: Goles a Favor → Puntos",
                               height=320)
        fig_reg.update_xaxes(title="Goles a favor")
        fig_reg.update_yaxes(title="Puntos")
        st.plotly_chart(fig_reg, use_container_width=True)


# ══════════════════════ TAB 4: SIMULADOR ══════════════════════
with tab4:
    st.markdown("#### 🔮 Simulador de rendimiento esperado")
    st.caption("Estima los puntos y la posición final según los parámetros ingresados")

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        sim_ppg   = st.slider("PPG esperado del DT", 1.2, 2.3, 1.75, step=0.05)
    with col_s2:
        sim_gf    = st.slider("Goles a favor esperados", 40, 90, 62)
    with col_s3:
        sim_stab  = st.slider("Índice de estabilidad táctica (1-10)", 1, 10, 7)

    sim_pts    = round(sim_ppg * 38)
    sim_gap    = max(0, 89 - sim_pts)
    sim_pos    = max(1, min(20, round(10 - (sim_pts - 58) / 4)))
    sim_ucl    = "Champions League ✅" if sim_pts >= 71 else ("Europa League ⚠️" if sim_pts >= 60 else "Nada 🔴")

    st.markdown("<br>", unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    with r1: st.metric("Puntos proyectados", sim_pts, delta=f"{sim_pts - 64:+d} vs baseline (Moyes)")
    with r2: st.metric("Posición estimada", f"{sim_pos}°")
    with r3: st.metric("Brecha vs campeón", f"{sim_gap} pts")
    with r4: st.metric("Clasificación europea", sim_ucl)

    # Gauge PPG
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=sim_ppg,
        delta={"reference": 1.64, "valueformat": ".2f"},
        title={"text": "PPG vs Media Histórica ManUtd (1.64)"},
        gauge={
            "axis": {"range": [1.0, 2.3], "tickcolor": "#8b949e"},
            "bar": {"color": COLORS["manutd"]},
            "steps": [
                {"range": [1.0, 1.5], "color": "rgba(247,129,102,0.3)"},
                {"range": [1.5, 1.8], "color": "rgba(227,179,65,0.3)"},
                {"range": [1.8, 2.3], "color": "rgba(63,185,80,0.3)"},
            ],
            "threshold": {"line": {"color": COLORS["champ"], "width": 2}, "value": 2.0},
            "bgcolor": "rgba(22,27,34,0.8)",
        },
        number={"font": {"color": COLORS["text"], "family": "Inter"}, "valueformat": ".2f"},
    ))
    fig_gauge.update_layout(**PLOTLY_THEME, height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🚀 Próximos Pasos — Escalado con IA")
    col_ai1, col_ai2 = st.columns(2)
    with col_ai1:
        st.markdown("""
        **Predicción de rendimiento**
        - Modelo XGBoost entrenado con datos de los últimos 30 años de la PL
        - Features: PPG del DT en clubes anteriores, inversión en mercado,
          estabilidad defensiva, índice de edad del plantel
        - Output: puntos proyectados para próxima temporada con IC 95%
        """)
    with col_ai2:
        st.markdown("""
        **Clustering de gestiones técnicas**
        - K-Means sobre vectores (PPG, GF, GA, posición, UCL exit)
        - Identifica perfiles: "estabilizador", "transición", "campeón"
        - Utilidad: matching de perfil DT con necesidad del club
        """)


# ─────────────────────────────── FOOTER ───────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#8b949e;font-size:.78rem;'>
  Álvaro Salinas Ortiz · Data Analyst ·
  <a href='https://github.com/alvarosalinaso/manchester-united-analisis' style='color:#58a6ff;'>GitHub</a> ·
  <a href='https://www.linkedin.com/in/alvaro-salinas-ortiz/' style='color:#58a6ff;'>LinkedIn</a>
</div>
""", unsafe_allow_html=True)

