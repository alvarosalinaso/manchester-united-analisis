"""
Manchester United — Performance Analytics Dashboard
Álvaro Salinas Ortiz | github.com/alvarosalinaso
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Man Utd · Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
:root {
  --bg:      #F8FAFC;
  --surface: #FFFFFF;
  --border:  #E2E8F0;
  --text-1:  #0F172A;
  --text-2:  #475569;
  --red:     #C41E3A;
  --red-l:   #FDECEA;
  --gold:    #B7960C;
  --gold-l:  #FEFCE8;
  --ok:      #15803D;
  --danger:  #B91C1C;
  --radius:  10px;
  --shadow:  0 1px 3px rgba(0,0,0,.08);
}
html,body,[class*="css"] { font-family: 'Inter', system-ui, sans-serif; }
.main, .block-container { background: var(--bg) !important; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1200px; }
section[data-testid="stSidebar"] { background: #1C0A0A !important; }
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown p { color: #FCA5A5 !important; font-size:.85rem !important; }
section[data-testid="stSidebar"] h2 { color: #FEF2F2 !important; font-size:1rem !important; font-weight:600 !important; }
.kpi { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius);
       padding:1.1rem 1.25rem; box-shadow:var(--shadow); }
.kpi-val   { font-size:1.9rem; font-weight:700; color:var(--text-1); line-height:1.1; }
.kpi-label { font-size:.7rem; font-weight:600; color:var(--text-2); text-transform:uppercase; letter-spacing:.08em; margin-top:.35rem; }
.kpi-delta { font-size:.78rem; font-weight:500; margin-top:.25rem; }
.kpi-delta.up   { color: var(--ok); }
.kpi-delta.down { color: var(--danger); }
.kpi-delta.neu  { color: var(--text-2); }
.sec-header { font-size:.7rem; font-weight:700; color:var(--text-2); text-transform:uppercase;
              letter-spacing:.1em; border-bottom:2px solid var(--red-l); padding-bottom:.4rem; margin:1.6rem 0 .9rem; }
</style>"""
st.markdown(CSS, unsafe_allow_html=True)

# ─── DATOS ────────────────────────────────────────────────────────────────────
@st.cache_data
def build_data():
    np.random.seed(42)
    MANAGERS = {
        "David Moyes":        range(2014,2015),
        "Louis van Gaal":     range(2015,2017),
        "José Mourinho":      range(2017,2019),
        "Ole G. Solskjær":    range(2019,2022),
        "Erik ten Hag (1a)":  range(2022,2023),
        "Erik ten Hag (2a)":  range(2023,2025),
    }
    BASE = {"David Moyes":64,"Louis van Gaal":70,"José Mourinho":69,
            "Ole G. Solskjær":66,"Erik ten Hag (1a)":58,"Erik ten Hag (2a)":44}

    def get_mgr(y):
        for m,r in MANAGERS.items():
            if y in r: return m
        return "Otro"

    seasons = []
    for yr in range(2014,2025):
        mgr = get_mgr(yr)
        pts = BASE.get(mgr,60) + np.random.randint(-5,6)
        gf  = int(pts*.82 + np.random.randint(-5,6))
        ga  = int(80 - pts*.55 + np.random.randint(-4,5))
        seasons.append({
            "season": f"{yr}/{str(yr+1)[-2:]}","year":yr,"manager":mgr,
            "points":pts,"goals_for":gf,"goals_against":ga,
            "xg":round(pts*.032+np.random.uniform(-.2,.2),2),
            "gd":gf-ga,"position":max(1,min(20,int(20-pts/5+np.random.randint(-1,2)))),
            "wins":int(pts/3*.75),"draws":int(pts/3*.25),"losses":int(38-pts/3),
        })
    df_s = pd.DataFrame(seasons)

    players = [
        {"player":"B. Fernandes","pos":"CAM","apps":32,"goals":8,"assists":10,"pass_acc":88.4,"xg":7.8,"xT":0.42,"market_val":70},
        {"player":"R. Højlund",  "pos":"ST", "apps":20,"goals":7,"assists":2, "pass_acc":83.1,"xg":8.9,"xT":0.18,"market_val":70},
        {"player":"K. Mainoo",   "pos":"CM", "apps":28,"goals":2,"assists":3, "pass_acc":85.7,"xg":1.8,"xT":0.24,"market_val":60},
        {"player":"A. Garnacho", "pos":"RW", "apps":34,"goals":7,"assists":6, "pass_acc":74.1,"xg":6.1,"xT":0.35,"market_val":55},
        {"player":"M. Ugarte",   "pos":"CDM","apps":22,"goals":0,"assists":1, "pass_acc":89.1,"xg":0.4,"xT":0.08,"market_val":50},
        {"player":"L. Martínez", "pos":"CB", "apps":29,"goals":1,"assists":1, "pass_acc":93.4,"xg":0.9,"xT":0.15,"market_val":60},
        {"player":"D. Dalot",    "pos":"RB", "apps":35,"goals":2,"assists":4, "pass_acc":84.1,"xg":1.5,"xT":0.22,"market_val":35},
        {"player":"A. Onana",    "pos":"GK", "apps":36,"goals":0,"assists":0, "pass_acc":72.4,"xg":0.0,"xT":0.02,"market_val":45},
        {"player":"Casemiro",    "pos":"CDM","apps":26,"goals":1,"assists":1, "pass_acc":86.5,"xg":0.8,"xT":0.11,"market_val":15},
        {"player":"A. Diallo",   "pos":"LW", "apps":22,"goals":5,"assists":3, "pass_acc":81.2,"xg":4.2,"xT":0.28,"market_val":40},
        {"player":"C. Eriksen",  "pos":"CM", "apps":24,"goals":1,"assists":4, "pass_acc":91.2,"xg":1.0,"xT":0.31,"market_val":12},
    ]
    df_p = pd.DataFrame(players)

    np.random.seed(7); pts_a=0; mds=[]
    for md in range(1,39):
        r   = np.random.choice(["V","E","D"],p=[.38,.22,.40])
        pts_a += 3 if r=="V" else 1 if r=="E" else 0
        mds.append({"jornada":md,"resultado":r,"pts_acc":pts_a,
                    "xg":round(np.random.uniform(.8,2.4),2),
                    "xga":round(np.random.uniform(.6,2.2),2),
                    "gf":np.random.poisson(1.3 if r!="D" else .8),
                    "ga":np.random.poisson(.8 if r=="V" else 1.5)})
    df_m = pd.DataFrame(mds)
    return df_s, df_p, df_m

df_seasons, df_players, df_matches = build_data()

PT = dict(
    template="plotly_white", paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="Inter, system-ui", color="#0F172A", size=12),
    margin=dict(t=44, b=30, l=10, r=10),
    colorway=["#C41E3A","#1E3A8A","#15803D","#B7960C","#7C3AED","#0891B2","#DC2626","#D97706"],
)

RED_SCALE = [[0,"#FEF2F2"],[.5,"#F87171"],[1,"#C41E3A"]]

def kpi(col, val, label, delta="", delta_cls="neu"):
    col.markdown(
        f"<div class='kpi'><div class='kpi-val'>{val}</div>"
        f"<div class='kpi-label'>{label}</div>"
        f"{'<div class=kpi-delta ' + delta_cls + '>' + delta + '</div>' if delta else ''}"
        f"</div>", unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚽ Man Utd Analytics")
    st.markdown("---")
    vista = st.selectbox("**Sección**", [
        "📅 Evolución histórica",
        "📊 Temporada 2024/25",
        "👤 Análisis de jugadores",
        "🎯 Comparativa radar",
    ])

    if vista == "📅 Evolución histórica":
        st.markdown("#### Filtros")
        mgrs_sel = st.multiselect("Entrenadores", df_seasons["manager"].unique().tolist(),
                                   default=df_seasons["manager"].unique().tolist())
        metrica  = st.selectbox("Métrica principal",
                                 ["points","goals_for","goals_against","xg","gd","position"],
                                 format_func=lambda x: {
                                     "points":"Puntos","goals_for":"Goles a favor",
                                     "goals_against":"Goles en contra","xg":"xG promedio",
                                     "gd":"Diferencia de goles","position":"Posición final"}[x])
        yr_range = st.slider("Temporadas", 2014, 2024, (2014, 2024))

    elif vista == "👤 Análisis de jugadores":
        pos_f = st.multiselect("Posición", df_players["pos"].unique().tolist(),
                                default=df_players["pos"].unique().tolist())
        eje_x = st.selectbox("Eje X", ["pass_acc","xg","xT","apps","market_val"],
                              format_func=lambda x: {"pass_acc":"Prec. pase %","xg":"xG total",
                                "xT":"xT generado","apps":"Partidos","market_val":"Valor (M€)"}[x])
        eje_y = st.selectbox("Eje Y", ["goals","assists","xg","xT","pass_acc"],
                              format_func=lambda x: {"goals":"Goles","assists":"Asistencias",
                                "xg":"xG total","xT":"xT","pass_acc":"Prec. pase %"}[x])

    elif vista == "🎯 Comparativa radar":
        psel = st.multiselect("Jugadores (máx 5)", df_players["player"].tolist(),
                               default=["B. Fernandes","K. Mainoo","M. Ugarte","R. Højlund","L. Martínez"])

    st.markdown("---")
    st.markdown("<p style='font-size:.75rem;color:#9CA3AF;'>Álvaro Salinas Ortiz<br>"
                "<a href='https://github.com/alvarosalinaso' style='color:#F87171;'>github.com/alvarosalinaso</a></p>",
                unsafe_allow_html=True)

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("# ⚽ Manchester United · Analytics")
st.divider()

# ─── VISTAS ───────────────────────────────────────────────────────────────────

if vista == "📅 Evolución histórica":
    dff = df_seasons[df_seasons["manager"].isin(mgrs_sel) &
                     df_seasons["year"].between(*yr_range)]
    if dff.empty:
        st.warning("Sin datos para la selección actual.")
        st.stop()

    c1,c2,c3,c4 = st.columns(4)
    kpi(c1, f"{dff['points'].mean():.0f}", "Pts prom. / temporada")
    kpi(c2, str(dff["goals_for"].sum()), "Goles marcados (total)")
    kpi(c3, f"{dff['position'].min()}°", "Mejor clasificación")
    kpi(c4, f"{dff['wins'].sum()}", "Victorias totales")

    st.markdown("<div class='sec-header'>Tendencia por temporada</div>", unsafe_allow_html=True)
    label_map = {"points":"Puntos","goals_for":"Goles a favor","goals_against":"Goles en contra",
                 "xg":"xG","gd":"Diferencia de goles","position":"Posición"}
    fig = px.line(dff, x="season", y=metrica, color="manager", markers=True,
                  title=f"{label_map[metrica]} por temporada — por entrenador",
                  labels={"season":"Temporada", metrica: label_map[metrica], "manager":"Entrenador"},
                  **PT)
    fig.update_layout(height=360, legend=dict(orientation="h", y=1.1, font_size=11))
    if metrica == "position": fig.update_yaxes(autorange="reversed", title="Posición (1=mejor)")
    st.plotly_chart(fig, use_container_width=True)

    ca, cb = st.columns(2)
    with ca:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Goles a favor",   x=dff["season"],y=dff["goals_for"],  marker_color="#C41E3A"))
        fig2.add_trace(go.Bar(name="Goles en contra", x=dff["season"],y=dff["goals_against"],marker_color="#94A3B8"))
        fig2.update_layout(barmode="group", title="Goles por temporada", height=300,
                           legend=dict(orientation="h", y=1.05, font_size=10), **PT)
        st.plotly_chart(fig2, use_container_width=True)
    with cb:
        fig3 = px.scatter(dff, x="xg", y="goals_for", color="manager", size="points",
                          hover_data=["season","points"],
                          title="xG esperado vs Goles reales",
                          labels={"xg":"xG promedio","goals_for":"Goles anotados","manager":"Entrenador"},
                          **PT)
        lim = max(dff["xg"].max()*34, dff["goals_for"].max())
        fig3.add_shape(type="line",x0=dff["xg"].min(),y0=dff["xg"].min()*30,
                       x1=dff["xg"].max(),y1=dff["xg"].max()*30,
                       line=dict(color="#94A3B8",dash="dash",width=1))
        fig3.update_layout(height=300, legend=dict(font_size=10))
        st.plotly_chart(fig3, use_container_width=True)

elif vista == "📊 Temporada 2024/25":
    V=len(df_matches[df_matches["resultado"]=="V"])
    E=len(df_matches[df_matches["resultado"]=="E"])
    D=len(df_matches[df_matches["resultado"]=="D"])
    pts_total = df_matches["pts_acc"].iloc[-1]

    c1,c2,c3,c4,c5 = st.columns(5)
    kpi(c1, str(pts_total),  "Puntos totales")
    kpi(c2, str(V),          "Victorias",  f"Ratio {V/38:.0%}", "up" if V>=14 else "down")
    kpi(c3, str(E),          "Empates")
    kpi(c4, str(D),          "Derrotas",   f"{D/38:.0%} de partidos", "down" if D>15 else "neu")
    kpi(c5, f"{df_matches['xg'].mean():.2f}", "xG promedio / partido")

    st.markdown("<div class='sec-header'>Acumulado de puntos — jornada a jornada</div>", unsafe_allow_html=True)
    color_res = {"V":"#15803D","E":"#B7960C","D":"#C41E3A"}
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_matches["jornada"], y=df_matches["pts_acc"], mode="lines+markers",
        line=dict(color="#C41E3A", width=2.5),
        marker=dict(size=8, color=[color_res[r] for r in df_matches["resultado"]],
                    line=dict(width=1, color="white")),
        hovertemplate="Jornada %{x}: %{y} pts<extra></extra>",
    ))
    fig.add_hline(y=72, line_dash="dot", line_color="#15803D",
                  annotation_text="Ref. Champions (~72 pts)", annotation_font_size=10)
    fig.update_layout(title="Verde = victoria · Amarillo = empate · Rojo = derrota",
                      xaxis_title="Jornada", yaxis_title="Puntos acumulados", height=340, **PT)
    st.plotly_chart(fig, use_container_width=True)

    ca, cb = st.columns(2)
    with ca:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_matches["jornada"], y=df_matches["xg"],
                              name="xG (ataque)", marker_color="#C41E3A", opacity=.8))
        fig2.add_trace(go.Bar(x=df_matches["jornada"], y=-df_matches["xga"],
                              name="xGA (defensa)", marker_color="#94A3B8", opacity=.8))
        fig2.add_hline(y=0, line_width=1, line_color="#0F172A")
        fig2.update_layout(barmode="overlay", title="xG ataque vs xGA defensa por jornada",
                           xaxis_title="Jornada", height=300,
                           legend=dict(orientation="h", y=1.05, font_size=10), **PT)
        st.plotly_chart(fig2, use_container_width=True)
    with cb:
        fig3 = go.Figure(go.Pie(
            labels=["Victorias","Empates","Derrotas"],
            values=[V,E,D], hole=.55,
            marker_colors=["#15803D","#B7960C","#C41E3A"],
            textfont_size=12,
        ))
        fig3.update_layout(title="Distribución de resultados 2024/25",
                           paper_bgcolor="white", height=300,
                           font=dict(family="Inter"))
        st.plotly_chart(fig3, use_container_width=True)

elif vista == "👤 Análisis de jugadores":
    dff = df_players[df_players["pos"].isin(pos_f)] if pos_f else df_players
    lm  = {"pass_acc":"Precisión pase %","xg":"xG total","xT":"xT generado",
           "apps":"Partidos jugados","market_val":"Valor mercado (M€)",
           "goals":"Goles","assists":"Asistencias"}
    fig = px.scatter(dff, x=eje_x, y=eje_y, color="pos", size="apps", text="player",
                     title=f"{lm.get(eje_x,eje_x)} vs {lm.get(eje_y,eje_y)}",
                     labels={eje_x:lm.get(eje_x,eje_x), eje_y:lm.get(eje_y,eje_y), "pos":"Posición"},
                     hover_data={"pass_acc":True,"xg":True,"market_val":True,"apps":True},
                     **PT)
    fig.update_traces(textposition="top center", marker=dict(line=dict(width=1,color="white")))
    fig.add_hline(y=dff[eje_y].mean(), line_dash="dot", line_color="#94A3B8",
                  annotation_text="Promedio", annotation_font_size=9)
    fig.add_vline(x=dff[eje_x].mean(), line_dash="dot", line_color="#94A3B8")
    fig.update_layout(height=460, legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='sec-header'>Tabla de jugadores</div>", unsafe_allow_html=True)
    show_cols = ["player","pos","apps","goals","assists","pass_acc","xg","xT","market_val"]
    display   = dff[show_cols].sort_values("market_val",ascending=False).reset_index(drop=True)
    display.columns = ["Jugador","Pos","Partidos","Goles","Asist.","Prec. Pase %","xG","xT","Valor (M€)"]
    st.dataframe(display, use_container_width=True, hide_index=True)

elif vista == "🎯 Comparativa radar":
    psel = (psel or [])[:5]
    if len(psel) < 2:
        st.info("Selecciona al menos 2 jugadores en el sidebar para comparar.")
        st.stop()

    METRICS = ["pass_acc","xg","goals","assists","xT","apps"]
    LABELS  = ["Prec. Pase","xG","Goles","Asist.","xT","Partidos"]
    dff = df_players.set_index("player")[METRICS]
    dff_n = (dff - dff.min()) / (dff.max() - dff.min() + .001)

    COLORS = ["#C41E3A","#1E3A8A","#15803D","#B7960C","#7C3AED"]
    fig = go.Figure()
    for i, p in enumerate(psel):
        if p not in dff_n.index: continue
        vals = dff_n.loc[p, METRICS].tolist() + [dff_n.loc[p, METRICS[0]]]
        lbs  = LABELS + [LABELS[0]]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=lbs, name=p,
            line=dict(color=COLORS[i%len(COLORS)], width=2.5),
            fill="toself", fillcolor=COLORS[i%len(COLORS)], opacity=.12,
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,1], tickfont_size=9, gridcolor="#E2E8F0"),
                   bgcolor="#FAFAFA"),
        paper_bgcolor="white",
        legend=dict(orientation="h", y=-0.15, font_size=11),
        title="Perfil comparativo de jugadores — valores normalizados (0=mín, 1=máx del plantel)",
        font=dict(family="Inter"), height=520,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='sec-header'>Valores reales</div>", unsafe_allow_html=True)
    disp = df_players[df_players["player"].isin(psel)][["player"]+METRICS].set_index("player")
    disp.columns = LABELS
    st.dataframe(disp.round(2), use_container_width=True)
