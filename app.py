import streamlit as st
import joblib

# Importaciones modulares internas (Clean Architecture)
from src.manutd_analysis.dashboard_data import cargar_datos_streamlit, kpi_globales, agrupar_por_entrenador
from src.manutd_analysis.dashboard_plots import (
    graficar_tendencia,
    graficar_eficiencia_dt,
    graficar_correlacion,
    graficar_regresion_gf
)

# ─────────────────────────────── CONFIG ───────────────────────────────
st.set_page_config(
    page_title="Manchester United · Performance Intelligence",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos minimalistas Narrativos
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .stApp { background-color: #0d1117; color: #e6edf3; }
    
    /* Headers de Sección con Estilo Narrativo */
    .section-header {
        font-weight: 800;
        font-size: 1.8rem;
        color: #ff4b4b;
        margin-top: 3rem;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid #30363d;
        padding-bottom: 0.5rem;
    }
    .section-text { font-size: 1.05rem; color: #8b949e; margin-bottom: 1.5rem; line-height: 1.6; }
    
    /* KPIs y Tarjetas */
    [data-testid="metric-container"] { background: #161b22 !important; border: 1px solid #30363d; border-radius: 12px; padding: 1rem; }
    [data-testid="stMetricValue"] { color: #ff4b4b !important; font-weight: 800 !important; }
    
    /* Panel IA */
    .ia-panel { background: #161b22; padding: 2rem; border-radius: 12px; border: 1px solid #30363d; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────── DATA LAYER ───────────────────────────────
try:
    df_f = cargar_datos_streamlit()
    kpis = kpi_globales(df_f)
    df_grp = agrupar_por_entrenador(df_f)
except Exception as e:
    st.error("Error crítico de carga de datos. Verifica la existencia de `data/raw/streamlit_data.csv`.")
    st.stop()

# ─────────────────────────────── SIDEBAR ───────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;margin-bottom:1.2rem;'>
      <img src="https://upload.wikimedia.org/wikipedia/en/thumb/7/7a/Manchester_United_FC_crest.svg/1200px-Manchester_United_FC_crest.svg.png" width="80">
      <div style='font-weight:800;font-size:1.2rem;color:#ff4b4b;margin-top:0.5rem;'>Manchester United</div>
      <div style='font-size:.8rem;color:#8b949e;'>Performance Intelligence · 2013-2024</div>
    </div>
    <hr>
    """, unsafe_allow_html=True)
    
    st.markdown("**🎛️ Filtros Globales del Reporte**")
    st.selectbox("Temporadas Analizadas", ["Totales (2014-2024)"])
    st.selectbox("Comparativa Histórica", ["Todos los Entrenadores"])
    
    st.markdown("---")
    st.markdown("**⚙️ Ajustes de Visualización**")
    t_comp = st.toggle("Modo comparativa vs PL Top 6")
    show_trend = st.toggle("Mostrar curva térmica de tendencia (LOWESS)", value=False)

# ─────────────────────────────── HERO SECTION ───────────────────────────────
st.markdown("<h1 style='margin-bottom:0;'>⚽ Manchester United · Diagnóstico Estructural</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size:1.1rem; color:#8b949e; margin-top:.2rem;'>Benchmarking directivo de la Premier League Post-Ferguson. Un análisis financiero-deportivo que expone las falencias estructurales detrás de más de una década de inestabilidad.</p><hr>", unsafe_allow_html=True)

# KPI ROW
cols = st.columns(5)
cols[0].metric("Temporadas Analizadas", f"{kpis['n_seasons']}")
cols[1].metric("Puntos Perdidos vs Campeón", f"{kpis['total_gap']}", f"↑ {kpis['total_gap']//kpis['n_seasons']} pts de brecha anual", delta_color="inverse")
cols[2].metric("Ritmo de Puntos (PPG)", f"{kpis['avg_ppg']:.2f}", "↓ Lejos del 1.97 de Mourinho", delta_color="inverse")
cols[3].metric("Costo Despidos / DTs", f"£{kpis['total_comp']}M", "Hoyo financiero", delta_color="inverse")
cols[4].metric("Aterrizaje Promedio PL", f"{kpis['avg_pos']:.1f}°")

# Paneles descriptivos iniciales
col1, col2 = st.columns(2)
with col1:
    st.info("💸 **£32.1M invertidos literalmente en despidos** de cuerpos técnicos (Moyes, Van Gaal, Mourinho, Solskjær, Ten Hag). Dinero muerto que equivale financieramente a perderse el fichaje de un jugador rotacional Élite por año.")
with col2:
    st.info("📉 **Gap Estadístico frente al Campeón:** A pesar de clasificar repetidas veces a Champions (Espejismo del Top 4), el United lleva promediando un abismo brutal de más de 20 puntos por temporada frente al equipo coronado de Inglaterra.")

# ─────────────────────────────── SECCIÓN 1 ───────────────────────────────
st.markdown("<div class='section-header'>1. Decadencia Histórica y la Brecha (Gap) 📊</div>", unsafe_allow_html=True)
st.markdown("<div class='section-text'>La métrica más cruda del éxito no son los puntos absolutos, sino la distancia con el número 1. Las <b>barras grises y rojas</b> muestran exactamente cuántos puntos le faltaron al club cada temporada para coronarse. Activa la <b>curva LOWESS paralela</b> en la barra lateral para evidenciar el estancamiento estructural sin fin en la última década. Las líneas verticales denotan roturas tácticas catastróficas (Despido del DT a mitad de torneo).</div>", unsafe_allow_html=True)

st.plotly_chart(graficar_tendencia(df_f, show_trend), use_container_width=True)

# ─────────────────────────────── SECCIÓN 2 ───────────────────────────────
st.markdown("<div class='section-header'>2. Análisis de Rentabilidad por Manager (PPG) 👔</div>", unsafe_allow_html=True)
st.markdown("<div class='section-text'>En el fútbol de élite mundial, si tu <b>PPG (Puntos por Partido)</b> cae debajo de la zona amarilla crítica (< 1.7), matemáticamente juegas a la ruleta rusa con la clasificación a Europa League. Observamos que José Mourinho fue empíricamente el entrenador con la maquinaria táctica más solvente del club post-Ferguson, aún a pesar del ruido mediático.</div>", unsafe_allow_html=True)

st.plotly_chart(graficar_eficiencia_dt(df_grp), use_container_width=True)
with st.expander("Ver desglose financiero y contractual de rendimiento por técnico"):
    st.dataframe(df_grp, use_container_width=True, hide_index=True)

# ─────────────────────────────── SECCIÓN 3 ───────────────────────────────
st.markdown("<div class='section-header'>3. Elasticidad Táctica y Correlaciones de Crisis 🧮</div>", unsafe_allow_html=True)
st.markdown("<div class='section-text'>¿El United falla por ser un flan en defensa o por un ataque anémico? La Inteligencia de Datos responde esta duda: <b>La Matriz de Correlación (izquierda)</b> demuestra estadísticamente que los goles en contra (`ga`) no tienen relación sólida directa con el hundimiento en la tabla. El problema es netamente ofensivo. <b>La Regresión (derecha)</b> demuestra esa altísima elasticidad matemática entre la falta de creatividad goleadora y el vacío de puntos obtenido al final de mayo.</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(graficar_correlacion(df_f), use_container_width=True)
with c2:
    st.plotly_chart(graficar_regresion_gf(df_f), use_container_width=True)

# ─────────────────────────────── SECCIÓN 4: MODELO ML ───────────────────────────────
st.markdown("<div class='section-header'>4. Simulador Algorítmico y Estrategia a Futuro 🔮</div>", unsafe_allow_html=True)
st.markdown("<div class='section-text'>La directiva de INEOS necesita proyectar a futuro. Modificando los deslizadores de la interfaz construimos un escenario del club para la siguiente temporada. Un algoritmo de Inteligencia Artificial (<b>Random Forest Regressor</b>) procesará miles de árboles de decisión en milisegundos usando el historial del Big-6 de Inglaterra y predecirá cuántos puntos finales obtendrá el Manchester United a fines de mayo.</div>", unsafe_allow_html=True)

st.markdown("<div class='ia-panel'>", unsafe_allow_html=True)
sc1, sc2, sc3 = st.columns(3)
exp_ppg = sc1.slider("Ritmo Exigido al DT (PPG Objetivo)", 1.4, 2.7, 1.8, 0.05)
exp_gf = sc2.slider("Productividad Ofensiva (Goles Anuales)", 40, 95, 60, 1)
est_score = sc3.slider("Grado de Estabilidad Táctica (1-10)", 1, 10, 5, 1)

st.markdown("<hr style='border-color:#30363d;'>", unsafe_allow_html=True)

try:
    model = joblib.load("models/ppg_simulator.pkl")
    import pandas as pd
    input_data = pd.DataFrame([{'ppg_esperado': exp_ppg, 'gf_esperado': exp_gf, 'estabilidad': est_score}])
    pts_pred = float(model.predict(input_data)[0])
    
    pred1, pred2 = st.columns(2)
    pred1.metric("⚖️ Puntos Absolutos Proyectados por IA", f"{pts_pred:.0f} pts", "Al finalizar las 38 fechas")
    
    status = "<span style='color:#2ea043;font-weight:bold;font-size:1.4rem'>🏆 Ritmo de Campeón</span>" if pts_pred > 85 else \
             "<span style='color:#e3b341;font-weight:bold;font-size:1.4rem'>⭐ Zona Champions League</span>" if pts_pred > 72 else \
             "<span style='color:#da3633;font-weight:bold;font-size:1.4rem'>✈️ Terreno de Europa League</span>" if pts_pred > 62 else \
             "<span style='color:#da3633;font-weight:bold;font-size:1.4rem'>❌ Crisis / Zona Media de Tabla</span>"
             
    pred2.markdown(f"**Veredicto Institucional:**<br>{status}", unsafe_allow_html=True)
    
except Exception as e:
    st.error(f"El modelo predictivo no pudo cargarse en este entorno. {e}")
st.markdown("</div>", unsafe_allow_html=True)
