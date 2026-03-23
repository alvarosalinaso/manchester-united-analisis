import streamlit as st, joblib, pandas as pd

from src.manutd_analysis.dashboard_data import cargar_datos_streamlit, kpi_globales, agrupar_por_entrenador
from src.manutd_analysis.dashboard_plots import graficar_tendencia, graficar_eficiencia_dt, graficar_correlacion, graficar_regresion_gf

st.set_page_config(page_title="Manchester United | Desastre Financiero", page_icon="⚽", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .section-header { font-weight: 800; font-size: 1.8rem; color: #ff4b4b; margin-top: 3rem; border-bottom: 1px solid #30363d; padding-bottom: 0.5rem; }
    .section-text { font-size: 1.05rem; color: #8b949e; margin-bottom: 1.5rem; }
    [data-testid="metric-container"] { background: #161b22 !important; border: 1px solid #30363d; border-radius: 8px; padding: 1rem; }
    [data-testid="stMetricValue"] { color: #ff4b4b !important; font-weight: 800 !important; }
    .ia-panel { background: #161b22; padding: 2rem; border-radius: 8px; border: 1px solid #30363d; }
</style>
""", unsafe_allow_html=True)

df_base = cargar_datos_streamlit()
kpi_dict = kpi_globales(df_base)
dt_agg = agrupar_por_entrenador(df_base)

with st.sidebar:
    st.markdown("<h2 style='color:#ff4b4b;text-align:center;'>Man Utd Stats</h2><hr>", unsafe_allow_html=True)
    st.selectbox("Rango", ["Totales (2014-2024)"])
    st.selectbox("Benchmark", ["Todos los DTs"])
    
    st.markdown("---")
    cmp_top6 = st.toggle("Verano Top 6")
    show_lowess = st.toggle("Curva Térmica (LOWESS)", value=False)

st.title("⚽ United: El Hueco Financiero")
st.markdown("Los números duros de una década quemando plata post-Ferguson. Foco puramente pragmático: resultados vs gastadero.")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Temporadas", f"{kpi_dict['n_seasons']}")
m2.metric("Gap Promedio Puntos", f"{kpi_dict['total_gap']} pts", delta_color="inverse")
m3.metric("Plata Quemada (Net Spend)", f"£{kpi_dict['total_net_spend']:.0f}M", delta_color="inverse")
m4.metric("Pos Promedio", f"{kpi_dict['avg_pos']:.1f}")

i1, i2 = st.columns(2)
with i1: st.info("💸 £32.1M literalmente a la basura en finiquitos. Dinero que te compra un mediocampista titular en Europa.")
with i2: st.info("📉 Ojo al Gap: Abismo superior a 20pts promediados con el campeón de turno, incluso si se entra a Champions raspando.")

st.markdown("<div class='section-header'>1. Estancamiento (Gap Histórico)</div>", unsafe_allow_html=True)
st.markdown("La distancia en puntos con el campeón (rojo/gris). Las líneas verticales son los parches (despido de técnico a medio torneo).", unsafe_allow_html=True)
st.plotly_chart(graficar_tendencia(df_base, show_lowess), use_container_width=True)

st.markdown("<div class='section-header'>2. Eficiencia Táctica (PPG)</div>", unsafe_allow_html=True)
st.markdown("PPG menor a 1.7 = ruleta rusa. Paradójicamente Mourinho, siendo el más resistido mediáticamente, sostuvo el mejor piso matemático.", unsafe_allow_html=True)
st.plotly_chart(graficar_eficiencia_dt(dt_agg), use_container_width=True)
with st.expander("Tabla Cruda"): st.dataframe(dt_agg, use_container_width=True, hide_index=True)

st.markdown("<div class='section-header'>3. Auditoría: Net Spend vs Puntos</div>", unsafe_allow_html=True)
st.markdown("¿Qué tanto rindieron las libras inyectadas por los Glazer e INEOS? El ratio clave de costo por punto.", unsafe_allow_html=True)
from src.manutd_analysis.dashboard_plots import graficar_costo_por_punto
st.plotly_chart(graficar_costo_por_punto(dt_agg), use_container_width=True)

st.markdown("<div class='section-header'>4. Correlación: Defensa vs Ataque</div>", unsafe_allow_html=True)
st.markdown("El drama estructural del club no está atrás, está arriba. La matriz confirma que comer goles asusta pero no te mata tanto como no meterlos (baja correlación con puntos).", unsafe_allow_html=True)

g1, g2 = st.columns(2)
with g1: st.plotly_chart(graficar_correlacion(df_base), use_container_width=True)
with g2: st.plotly_chart(graficar_regresion_gf(df_base), use_container_width=True)

st.markdown("<div class='section-header'>5. Proyector Algorítmico ML</div>", unsafe_allow_html=True)
st.markdown("<div class='ia-panel'>", unsafe_allow_html=True)
s1, s2, s3 = st.columns(3)
t_ppg = s1.slider("Target PPG", 1.4, 2.7, 1.8, 0.05)
t_gf = s2.slider("Goles Proyectados", 40, 95, 60, 1)
t_est = s3.slider("Score Estabilidad (1-10)", 1, 10, 5, 1)
st.markdown("<hr>", unsafe_allow_html=True)

try:
    rf = joblib.load("models/ppg_simulator.pkl")
    p_pts = float(rf.predict(pd.DataFrame([{'ppg_esperado': t_ppg, 'gf_esperado': t_gf, 'estabilidad': t_est}]))[0])
    
    r1, r2 = st.columns(2)
    r1.metric("Proyección Final", f"{p_pts:.0f} pts")
    
    st_tag = "<span style='color:#2ea043;font-weight:bold;'>🏆 Candidato PL</span>" if p_pts > 85 else \
             "<span style='color:#e3b341;font-weight:bold;'>⭐ Zona Champions</span>" if p_pts > 72 else \
             "<span style='color:#da3633;font-weight:bold;'>✈️ Terreno Europa</span>" if p_pts > 62 else \
             "<span style='color:#da3633;font-weight:bold;'>❌ Rellenando Tabla</span>"
    r2.markdown(f"**Tier:**<br>{st_tag}", unsafe_allow_html=True)
except Exception as e: st.error("Sin modelo RF cargado.")
st.markdown("</div>", unsafe_allow_html=True)
