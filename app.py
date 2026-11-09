"""Dashboard interactivo (Streamlit + Plotly) sobre el pipeline ``manutd_analysis``.

Ejecutar::

    streamlit run app.py

La app no duplica lógica: llama a :func:`manutd_analysis.pipeline.compute`,
la misma función que alimenta los reportes y el README.
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from manutd_analysis.config import ProjectPaths
from manutd_analysis.data_loader import DataLoadError
from manutd_analysis.logging_config import setup_logging
from manutd_analysis.metrics import safe_divide, stability_comparison
from manutd_analysis.pipeline import PipelineResult, compute
from manutd_analysis.validator import SchemaError

setup_logging("WARNING")
logger = logging.getLogger("app")

UTD_RED = "#c0392b"
NEUTRAL = "#7f8c8d"
CHAMPION = "#2c3e50"

st.set_page_config(page_title="Man Utd 2014-2024 · Costo de la inestabilidad", layout="wide")


@st.cache_data(show_spinner="Ejecutando pipeline…")
def run_pipeline(pl_bytes: bytes | None) -> PipelineResult:
    """Ejecuta el pipeline sobre los datos del repo o sobre un CSV subido por el usuario."""
    if pl_bytes is None:
        return compute()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "pl_tables.csv"
        path.write_bytes(pl_bytes)
        return compute(pl_csv=path, passing_csv=ProjectPaths.default().passing_csv)


# ── Barra lateral ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Fuente de datos")
    uploaded = st.file_uploader(
        "Tablas finales PL (CSV, opcional)",
        type="csv",
        help="Mismo esquema que data/pl-tables-1993-2024.csv. Se valida antes de calcular.",
    )
    st.caption("Sin archivo se usan las tablas oficiales 1993-2024 incluidas en el repositorio.")
    st.divider()
    st.markdown(
        "**Álvaro Salinas Ortiz**  \nAnalista de Datos y Operaciones  \n"
        "[GitHub](https://github.com/alvarosalinaso/manchester-united-analisis) · "
        "[LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz)"
    )

try:
    result = run_pipeline(uploaded.getvalue() if uploaded else None)
except (DataLoadError, SchemaError) as exc:
    st.error(f"Los datos no superaron la validación: {exc}")
    st.stop()

f = result.findings
kpis = result.kpis

# ── Encabezado y KPIs ─────────────────────────────────────────────────────────
st.title("Manchester United 2014-2024: el costo de la inestabilidad técnica")
st.caption(
    f"{f['n_temporadas']} temporadas · {f['n_entrenadores']} entrenadores titulares · "
    f"{f['n_temporadas_transicion']} temporadas con relevo a mitad de curso"
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Brecha media vs campeón", f"{f['brecha_media']:.1f} pts", help="Por temporada")
c2.metric(
    "Costo de un relevo",
    f"−{f['costo_inestabilidad']:.1f} pts",
    help="Puntos de una temporada con relevo vs una con DT único",
)
c3.metric(
    "PPG United vs campeón",
    f"{f['ppg_promedio']:.2f}",
    f"{f['ppg_promedio'] - f['ppg_campeon_promedio']:+.2f}",
)
c4.metric("Temporadas en Top 4", f"{f['temporadas_top4']} / {f['n_temporadas']}")

tab_gap, tab_mgr, tab_change, tab_pass = st.tabs(
    ["Brecha estructural", "Entrenadores", "Cambios de DT", "Pases 2024-25"]
)

# ── Brecha estructural ────────────────────────────────────────────────────────
with tab_gap:
    champ_ppg = safe_divide(kpis["pts_champ"], kpis["played"])
    fig = go.Figure()
    fig.add_scatter(
        x=kpis["año"], y=champ_ppg, name="Campeón", line={"color": CHAMPION, "dash": "dash"}
    )
    fig.add_scatter(
        x=kpis["año"],
        y=kpis["ppg"],
        name="Manchester United",
        line={"color": UTD_RED, "width": 3},
        customdata=kpis[["entrenador"]],
        hovertemplate="%{x}: %{y:.2f} PPG<br>%{customdata[0]}<extra></extra>",
    )
    fig.add_scatter(
        x=result.benchmark["temporada"],
        y=result.benchmark["pl_avg_ppg_sin_utd"],
        name="Media PL (sin United)",
        line={"color": NEUTRAL},
    )
    fig.update_layout(
        title="Puntos por partido por temporada", yaxis_title="PPG", hovermode="x unified"
    )
    st.plotly_chart(fig, width="stretch")

    bar = px.bar(
        kpis,
        x="año",
        y="brecha_puntos",
        color="es_transicion",
        color_discrete_map={False: NEUTRAL, True: UTD_RED},
        labels={
            "brecha_puntos": "Puntos detrás del campeón",
            "año": "Temporada",
            "es_transicion": "Relevo de DT",
        },
        title="Brecha con el campeón (rojo = temporada con relevo de DT)",
    )
    bar.add_hline(
        y=f["brecha_media"], line_dash="dot", annotation_text=f"media {f['brecha_media']:.1f}"
    )
    st.plotly_chart(bar, width="stretch")

# ── Entrenadores ──────────────────────────────────────────────────────────────
with tab_mgr:
    left, right = st.columns([3, 2])
    with left:
        summary = result.managers.reset_index(names="entrenador")
        scatter = px.scatter(
            summary,
            x="goles_promedio",
            y="eficiencia",
            size="temporadas",
            text="entrenador",
            color="ppg",
            color_continuous_scale="Reds",
            labels={
                "goles_promedio": "Goles a favor por temporada",
                "eficiencia": "Puntos por gol",
                "ppg": "PPG",
            },
            title="Volumen ofensivo vs eficiencia por entrenador",
        )
        scatter.update_traces(textposition="top center")
        st.plotly_chart(scatter, width="stretch")
    with right:
        comp = stability_comparison(kpis)
        st.subheader("Estable vs relevo")
        st.dataframe(comp, width="stretch")
        st.caption(
            "Promedios por temporada. Las temporadas con relevo incluyen la peor brecha del período."
        )
    st.dataframe(result.managers, width="stretch")

# ── Cambios de DT ─────────────────────────────────────────────────────────────
with tab_change:
    placebo = result.before_after.get("placebo_test")
    if placebo:
        changes = pd.DataFrame(placebo["per_change"])
        fig = px.bar(
            changes,
            x="change",
            y="delta_points",
            color="delta_points",
            color_continuous_scale=["#c0392b", "#ecf0f1", "#27ae60"],
            color_continuous_midpoint=0,
            hover_data=["p_value_placebo"],
            labels={"change": "Cambio", "delta_points": "Δ pts (3 temp. post − pre)"},
            title="Puntos medios antes y después de cada cambio de entrenador",
        )
        st.plotly_chart(fig, width="stretch")
        st.info(
            f"{placebo['n_significant']} de {placebo['n_changes_tested']} cambios superan el test "
            f"placebo ({placebo['n_simulations']} cortes aleatorios, semilla {placebo['seed']}). "
            "Lectura: cambiar de DT no produjo mejoras sostenidas; el costo aparece en la temporada del relevo."
        )
    st.json(result.stats, expanded=False)

# ── Pases ─────────────────────────────────────────────────────────────────────
with tab_pass:
    passing = result.passing
    fig = px.scatter(
        passing,
        x="prgp_90",
        y="kp_90",
        size="min_90s",
        color="pos",
        hover_name="jugador",
        labels={
            "prgp_90": "Pases progresivos / 90'",
            "kp_90": "Pases clave / 90'",
            "pos": "Posición",
        },
        title="Progresión vs creación, plantel 2024-25 (mín. 900 minutos)",
    )
    st.plotly_chart(fig, width="stretch")
    st.dataframe(passing, width="stretch", hide_index=True)
    st.caption("Fuente: FBref (Opta). Percentiles internos del plantel.")
