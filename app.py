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

# Estilos minimalistas
st.markdown("""
<style>
    .metric-value { font-size: 2rem !important; font-weight: 700; color: #ff4b4b; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px; border-radius: 4px 4px 0 0; background-color: #1e1e1e; color: #a0a0a0;
    }
    .stTabs [aria-selected="true"] { background-color: #ff4b4b; color: #ffffff !important; font-weight: bold; }
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
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7a/Manchester_United_FC_crest.svg/1200px-Manchester_United_FC_crest.svg.png", width=80)
    st.markdown("### Performance Intelligence")
    st.caption("Manchester United · 2013-2024")
    st.markdown("---")
    
    st.selectbox("Temporadas", ["Totales (2014-2024)"])
    st.selectbox("Entrenadores", ["Todos los Entrenadores"])
    
    t_comp = st.toggle("Modo comparativa vs PL Top 6")
    show_trend = st.toggle("Mostrar línea de tendencia", value=False)

# ─────────────────────────────── HEADER ───────────────────────────────
st.title("⚽ Manchester United · Performance Intelligence 🔗")
st.markdown("<small>Benchmarking directivo - Premier League 2013-2024 - Herramienta de decisión deportiva</small>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────── KPI ROW ───────────────────────────────
cols = st.columns(5)
cols[0].metric("Temporadas analizadas", f"{kpis['n_seasons']}")
cols[1].metric("Puntos perdidos vs campeón", f"{kpis['total_gap']}", f"↑ {kpis['total_gap']//kpis['n_seasons']} pts/temporada", delta_color="inverse")
cols[2].metric("PPG promedio", f"{kpis['avg_ppg']:.2f}", "↓ vs 1.97 (Mourinho)", delta_color="inverse")
cols[3].metric("Coste indemnizaciones", f"£{kpis['total_comp']}M", "↑ 10 años", delta_color="inverse")
cols[4].metric("Posición promedio PL", f"{kpis['avg_pos']:.1f}°")

# Paneles descriptivos
col1, col2 = st.columns(2)
with col1:
    st.info("ℹ️ **Costo de Indemnizaciones:** £32.1M invertidos solo en despidos de cuerpo técnico (Moyes, Van Gaal, Mourinho, Solskjær). Esto equivale aproximadamente al presupuesto de transferencia de un jugador rotacional TOP por temporada, que se pierde sin retorno en la cancha.")
with col2:
    st.info("ℹ️ **Brecha vs Campeón (Gap):** Frecuentemente el United ha reportado un falso \"progreso\" al quedar en el Top 4, pero la brecha real de puntos frente a los campeones promedia más de 20 puntos por temporada. El objetivo es recortar la brecha, no solo subir de posición.")

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────── TABS ───────────────────────────────
t1, t2, t3, t4 = st.tabs([
    "📊 Rendimiento Histórico", 
    "👔 Análisis por Entrenador", 
    "🧮 Diagnóstico Sistémico", 
    "🔮 Proyección & Simulador de IA"
])

# ══════════════════════ TAB 1 ══════════════════════
with t1:
    st.plotly_chart(graficar_tendencia(df_f, show_trend), use_container_width=True)
    with st.expander("📈 Entendiendo la Evolución de Puntos y Goles"):
        st.markdown("""
        *   **Barras Rojas (Gap):** Representan estadísticamente el diferencial entre el M. United y el ganador de la PL esa métrica exacta. Notablemente, las reducciones de la barra rara vez se mantienen tras dos temporadas.
        *   **Línea Punteada Verde (Diferencia Gol):** La solvencia real no se esconde en los puntos absolutos, a menudo alterados por suerte en partidos cerrados, sino en la diferencia de goles.
        *   **Línea Azul Clara (LOWESS):** Activar **Mostrar línea de tendencia** en la barra lateral aplica un suavizado estadístico 'Lowess'. Muestra que, a largo plazo, la curva del United está estancada.
        """)

# ══════════════════════ TAB 2 ══════════════════════
with t2:
    st.plotly_chart(graficar_eficiencia_dt(df_grp), use_container_width=True)
    with st.expander("👔 Interpretando el PPG y la Evaluación del Técnico"):
        st.markdown("""
        *   **El Valor PPG (Points Per Game):** Una métrica estándar en análisis de élite. 
            *   Un PPG `> 2.1` indica ritmo de campeón real.
            *   Un PPG `> 1.8` es la base mínima para entrar consistentemente a Champions League.
            *   Un PPG `< 1.7` está en la *Zona de Riesgo*, donde la irregularidad táctica no asegura torneos europeos y acelera el despido (línea roja segmentada).
        *   Mourinho es empíricamente el entrenador con mejor PPG histórico post-Ferguson, aún con altas fricciones mediáticas.
        """)
    st.dataframe(df_grp, use_container_width=True, hide_index=True)

# ══════════════════════ TAB 3 ══════════════════════
with t3:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(graficar_correlacion(df_f), use_container_width=True)
        with st.expander("🎲 ¿Cómo leer esta Matriz de Correlación?"):
            st.markdown("""
            *   Valores cercanos a `1.0` (rojo oscuro) = Fuerte relación directa (Ej: Goles favor suben = Puntos suben).
            *   Valores negativos `-1.0` (azul) = Relación inversa.
            *   **Insight crítico:** La variable `ga` (Goles en contra) tiene nula correlación útil en este cuadro del United. La crisis no es defender peor, sino la masiva inestabilidad de la estructura general en las transiciones (bajos Goles y muchas pérdidas ineficientes).
            """)
    with c2:
        st.plotly_chart(graficar_regresion_gf(df_f), use_container_width=True)
        with st.expander("📊 Elasticidad Ofensiva (Regresión Simple)"):
            st.markdown("""
            *   La línea recta es una predicción lineal (OLS). Cuanto más agrupados los puntos cerca de la línea (un alto R² estadístico), más predictivo es el modelo subyacente.
            *   Muestra cuántos "Puntos" marginales genera cada "Gol" anotado bajo la estructura del United (alta dependencia).
            """)

# ══════════════════════ TAB 4: SIMULADOR & MACHINE LEARNING ══════════════════════
with t4:
    st.subheader("⚖️ Simulador Predictivo con Machine Learning (Random Forest)")
    st.markdown("""
    Esta herramienta calcula indirectamente los puntos finales proyectados utilizando un modelo **RandomForestRegressor** `.pkl` entrenado en base a tendencias de eficiencia estadística del club y del entorno de la Premier League.
    Mueva los parámetros tácticos directivos para evaluar los techos de rendimiento.
    """)
    
    sc1, sc2, sc3 = st.columns(3)
    exp_ppg = sc1.slider("PPG Proyectado del Entrenador", 1.4, 2.7, 1.8, 0.05)
    exp_gf = sc2.slider("Expectativa de Goles a Favor (Temp)", 40, 95, 60, 1)
    est_score = sc3.slider("Índice de Estabilidad Táctica (1-10)", 1, 10, 5, 1)
    
    st.markdown("---")
    
    try:
        model = joblib.load("models/ppg_simulator.pkl")
        
        import pandas as pd
        input_data = pd.DataFrame([{
            'ppg_esperado': exp_ppg,
            'gf_esperado': exp_gf,
            'estabilidad': est_score
        }])
        
        pts_pred = float(model.predict(input_data)[0])
        
        pred1, pred2 = st.columns(2)
        pred1.metric("🔮 Puntos Simulados al final de temporada (ML Model)", f"{pts_pred:.0f} pts")
        
        status = "🟢 Ritmo de Campeón" if pts_pred > 85 else \
                 "🟡 Zona Champions" if pts_pred > 72 else \
                 "🟠 Europa League" if pts_pred > 62 else "🔴 Zona Media Baja"
        
        pred2.metric("🎯 Diagnóstico Contextual", status)
        
    except Exception as e:
        st.error(f"El modelo no pudo cargarse. Error: {e}")

st.markdown("---")
st.markdown("🛠️ Arquitectura Modularizada + Machine Learning Integration")
