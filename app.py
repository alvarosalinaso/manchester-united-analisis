import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Man Utd · Analytics", page_icon="⚽", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;800&family=Inter:wght@300;400;500&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;background:#f0f4f0;}
.block-container{padding-top:1.5rem;background:#f0f4f0;}
h1,h2,h3{font-family:'Syne',sans-serif;font-weight:800;color:#1b3a1f;}
.kpi{background:#fff;border-radius:14px;padding:1.1rem 1.3rem;border:1.5px solid #d6e8d6;box-shadow:0 2px 8px rgba(27,58,31,.06);}
.kpi-v{font-size:2.1rem;font-weight:800;color:#2d7a3a;letter-spacing:-1px;}
.kpi-l{font-size:0.68rem;color:#6b7c6d;text-transform:uppercase;letter-spacing:1.5px;margin-top:3px;}
section[data-testid="stSidebar"]{background:#1b3a1f!important;}
section[data-testid="stSidebar"] *{color:#d4edda!important;}
section[data-testid="stSidebar"] .stSelectbox>div>div{background:#2d5a32!important;color:#d4edda!important;}
</style>""", unsafe_allow_html=True)

np.random.seed(42)
MANAGERS={"David Moyes":range(2014,2015),"Louis van Gaal":range(2015,2017),
           "José Mourinho":range(2017,2019),"Ole Gunnar Solskjær":range(2019,2022),
           "Erik ten Hag (1a)":range(2022,2023),"Erik ten Hag (2a)":range(2023,2025)}
BASE_PTS={"David Moyes":64,"Louis van Gaal":70,"José Mourinho":69,
          "Ole Gunnar Solskjær":66,"Erik ten Hag (1a)":58,"Erik ten Hag (2a)":44}

def get_mgr(y):
    for m,r in MANAGERS.items():
        if y in r: return m
    return "Otro"

seasons=[]
for yr in range(2014,2025):
    mgr=get_mgr(yr)
    pts=BASE_PTS.get(mgr,60)+np.random.randint(-5,6)
    gf=int(pts*0.82+np.random.randint(-5,6))
    ga=int(80-pts*0.55+np.random.randint(-4,5))
    seasons.append({"season":f"{yr}/{str(yr+1)[-2:]}","year":yr,"manager":mgr,
        "points":pts,"goals_for":gf,"goals_against":ga,
        "xg":round(pts*0.032+np.random.uniform(-0.2,0.2),2),
        "gd":gf-ga,"position":max(1,min(20,int(20-pts/5+np.random.randint(-1,2)))),
        "wins":int(pts/3*0.75),"draws":int(pts/3*0.25),"losses":int(38-pts/3)})
df=pd.DataFrame(seasons)

PLAYERS=[{"player":"B. Fernandes","pos":"CAM","apps":32,"goals":8,"assists":10,"pass_acc":88.4,"xg":7.8,"market_value":70},
         {"player":"R. Højlund","pos":"ST","apps":20,"goals":7,"assists":2,"pass_acc":83.1,"xg":8.9,"market_value":70},
         {"player":"K. Mainoo","pos":"CM","apps":28,"goals":2,"assists":3,"pass_acc":85.7,"xg":1.8,"market_value":60},
         {"player":"A. Garnacho","pos":"RW","apps":34,"goals":7,"assists":6,"pass_acc":74.1,"xg":6.1,"market_value":55},
         {"player":"M. Ugarte","pos":"CDM","apps":22,"goals":0,"assists":1,"pass_acc":89.1,"xg":0.4,"market_value":50},
         {"player":"L. Martínez","pos":"CB","apps":29,"goals":1,"assists":1,"pass_acc":93.4,"xg":0.9,"market_value":60},
         {"player":"D. Dalot","pos":"RB","apps":35,"goals":2,"assists":4,"pass_acc":84.1,"xg":1.5,"market_value":35},
         {"player":"A. Onana","pos":"GK","apps":36,"goals":0,"assists":0,"pass_acc":72.4,"xg":0.0,"market_value":45},
         {"player":"Casemiro","pos":"CDM","apps":26,"goals":1,"assists":1,"pass_acc":86.5,"xg":0.8,"market_value":15},
         {"player":"A. Diallo","pos":"LW","apps":22,"goals":5,"assists":3,"pass_acc":81.2,"xg":4.2,"market_value":40},
         {"player":"C. Eriksen","pos":"CM","apps":24,"goals":1,"assists":4,"pass_acc":91.2,"xg":1.0,"market_value":12}]
dfp=pd.DataFrame(PLAYERS)

np.random.seed(7)
mds,pts_a=[],0
for md in range(1,39):
    r=np.random.choice(["W","D","L"],p=[0.38,0.22,0.40])
    pts_a+=(3 if r=="W" else 1 if r=="D" else 0)
    mds.append({"matchday":md,"result":r,"pts_acc":pts_a,
        "xg":round(np.random.uniform(0.8,2.4),2),"xga":round(np.random.uniform(0.6,2.2),2)})
dfm=pd.DataFrame(mds)

PALETTE=["#2d7a3a","#52b369","#8fd4a0","#c1e8c9","#f5c518","#e8913a","#c0392b","#2980b9"]

with st.sidebar:
    st.markdown("## ⚽ Panel de control")
    vista=st.selectbox("Vista",["Evolución histórica","Rendimiento 24/25","Jugadores","Comparativa radar"])
    if vista=="Evolución histórica":
        mgrs=st.multiselect("Entrenadores",list(MANAGERS.keys()),default=list(MANAGERS.keys()))
        metrica=st.selectbox("Métrica",["points","goals_for","goals_against","xg","gd","position"])
        yr_range=st.slider("Años",2014,2024,(2014,2024))
    elif vista=="Jugadores":
        pos_f=st.multiselect("Posición",dfp["pos"].unique().tolist(),default=dfp["pos"].unique().tolist())
        eje_x=st.selectbox("Eje X",["pass_acc","xg","apps","market_value"])
        eje_y=st.selectbox("Eje Y",["goals","assists","xg","pass_acc","market_value"])
    elif vista=="Comparativa radar":
        psel=st.multiselect("Jugadores (máx 5)",dfp["player"].tolist(),
            default=["B. Fernandes","K. Mainoo","M. Ugarte","R. Højlund","L. Martínez"])

st.markdown("# ⚽ Manchester United Analytics")
st.markdown(f"### {vista}")
st.divider()

if vista=="Evolución histórica":
    dff=df[(df["manager"].isin(mgrs))&(df["year"]>=yr_range[0])&(df["year"]<=yr_range[1])]
    c1,c2,c3,c4=st.columns(4)
    for col,val,lab in zip([c1,c2,c3,c4],
        [f"{dff['points'].mean():.0f}",f"{dff['goals_for'].sum()}",f"{dff['position'].min()}°",f"{dff['wins'].sum()}"],
        ["Pts promedio","Goles totales","Mejor posición","Victorias totales"]):
        col.markdown(f"<div class='kpi'><div class='kpi-v'>{val}</div><div class='kpi-l'>{lab}</div></div>",unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    labs={"points":"Puntos","goals_for":"Goles a favor","goals_against":"Goles en contra","xg":"xG","gd":"Diferencia goles","position":"Posición"}
    fig=px.line(dff,x="season",y=metrica,color="manager",markers=True,
                title=f"{labs[metrica]} por temporada",color_discrete_sequence=PALETTE)
    fig.update_layout(plot_bgcolor="#fff",paper_bgcolor="#f0f4f0",height=360,
                      font=dict(family="Inter"),legend=dict(orientation="h",y=1.1))
    if metrica=="position": fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig,use_container_width=True)
    ca,cb=st.columns(2)
    with ca:
        fig2=go.Figure()
        fig2.add_trace(go.Bar(name="A favor",x=dff["season"],y=dff["goals_for"],marker_color="#2d7a3a"))
        fig2.add_trace(go.Bar(name="En contra",x=dff["season"],y=dff["goals_against"],marker_color="#e8913a"))
        fig2.update_layout(barmode="group",plot_bgcolor="#fff",paper_bgcolor="#f0f4f0",
                           height=300,font=dict(family="Inter"),title="Goles por temporada")
        st.plotly_chart(fig2,use_container_width=True)
    with cb:
        fig3=px.scatter(dff,x="xg",y="goals_for",color="manager",size="points",
                        hover_data=["season","manager"],title="xG vs Goles reales",
                        color_discrete_sequence=PALETTE)
        fig3.update_layout(plot_bgcolor="#fff",paper_bgcolor="#f0f4f0",height=300,font=dict(family="Inter"))
        st.plotly_chart(fig3,use_container_width=True)

elif vista=="Rendimiento 24/25":
    wins=len(dfm[dfm["result"]=="W"]); draws=len(dfm[dfm["result"]=="D"]); losses=len(dfm[dfm["result"]=="L"])
    c1,c2,c3,c4,c5=st.columns(5)
    for col,val,lab in zip([c1,c2,c3,c4,c5],
        [dfm["pts_acc"].iloc[-1],wins,draws,losses,f"{dfm['xg'].mean():.2f}"],
        ["Puntos totales","Victorias","Empates","Derrotas","xG promedio"]):
        col.markdown(f"<div class='kpi'><div class='kpi-v'>{val}</div><div class='kpi-l'>{lab}</div></div>",unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=dfm["matchday"],y=dfm["pts_acc"],mode="lines+markers",
        name="Puntos acumulados",line=dict(color="#2d7a3a",width=3),
        marker=dict(size=7,color=["#2d7a3a" if r=="W" else "#f5c518" if r=="D" else "#c0392b" for r in dfm["result"]])))
    fig.add_hline(y=72,line_dash="dash",line_color="#8fd4a0",annotation_text="Ref. Top 4 (~72 pts)")
    fig.update_layout(plot_bgcolor="#fff",paper_bgcolor="#f0f4f0",height=340,
                      title="Acumulado de puntos — jornada a jornada",font=dict(family="Inter"))
    st.plotly_chart(fig,use_container_width=True)
    ca,cb=st.columns(2)
    with ca:
        fig2=go.Figure()
        fig2.add_trace(go.Bar(x=dfm["matchday"],y=dfm["xg"],name="xG",marker_color="#52b369",opacity=0.85))
        fig2.add_trace(go.Bar(x=dfm["matchday"],y=-dfm["xga"],name="xGA",marker_color="#e8913a",opacity=0.85))
        fig2.update_layout(barmode="overlay",plot_bgcolor="#fff",paper_bgcolor="#f0f4f0",
                           title="xG ofensivo vs defensivo",height=300,font=dict(family="Inter"))
        st.plotly_chart(fig2,use_container_width=True)
    with cb:
        fig3=go.Figure(go.Pie(labels=["Victorias","Empates","Derrotas"],values=[wins,draws,losses],
            hole=0.55,marker_colors=["#2d7a3a","#f5c518","#e8e0d5"]))
        fig3.update_layout(paper_bgcolor="#f0f4f0",title="Distribución resultados",height=300,font=dict(family="Inter"))
        st.plotly_chart(fig3,use_container_width=True)

elif vista=="Jugadores":
    dff=dfp[dfp["pos"].isin(pos_f)]
    lm={"pass_acc":"Precisión pase %","xg":"xG total","apps":"Partidos","market_value":"Valor (M€)",
        "goals":"Goles","assists":"Asistencias"}
    fig=px.scatter(dff,x=eje_x,y=eje_y,color="pos",size="apps",text="player",
                   title=f"{lm.get(eje_x,eje_x)} vs {lm.get(eje_y,eje_y)}",
                   color_discrete_sequence=PALETTE)
    fig.update_traces(textposition="top center",marker=dict(line=dict(width=1,color="white")))
    fig.update_layout(plot_bgcolor="#fff",paper_bgcolor="#f0f4f0",height=460,font=dict(family="Inter"))
    st.plotly_chart(fig,use_container_width=True)
    st.dataframe(dff[["player","pos","apps","goals","assists","pass_acc","xg","market_value"]]
                 .sort_values("market_value",ascending=False).reset_index(drop=True),use_container_width=True)

elif vista=="Comparativa radar":
    psel=psel[:5]
    metrics_r=["pass_acc","xg","goals","assists","apps","market_value"]
    labels_r=["Prec. Pase","xG","Goles","Asist.","Partidos","Valor"]
    dff=dfp[dfp["player"].isin(psel)].set_index("player")
    dfn=(dff[metrics_r]-dff[metrics_r].min())/(dff[metrics_r].max()-dff[metrics_r].min()+0.001)
    colors_r=["#2d7a3a","#f5c518","#c0392b","#2980b9","#e8913a"]
    fig=go.Figure()
    for i,p in enumerate(psel):
        if p not in dfn.index: continue
        vals=dfn.loc[p,metrics_r].tolist()
        vals+=[vals[0]]
        fig.add_trace(go.Scatterpolar(r=vals,theta=labels_r+[labels_r[0]],name=p,
            line=dict(color=colors_r[i%len(colors_r)],width=2),
            fill="toself",fillcolor=colors_r[i%len(colors_r)],opacity=0.15))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,1]),bgcolor="#f0f4f0"),
                      paper_bgcolor="#f0f4f0",height=500,font=dict(family="Inter"),
                      title="Radar comparativo de jugadores")
    st.plotly_chart(fig,use_container_width=True)
