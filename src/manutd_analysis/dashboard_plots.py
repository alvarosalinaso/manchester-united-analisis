import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#e6edf3",
    hoverlabel=dict(bgcolor="#161b22", font_size=12, font_color="#e6edf3"),
    margin=dict(l=40, r=20, t=60, b=40)
)

def graficar_tendencia(df, trendline=False):
    fig_pts = px.line(df, x="season", y="points", markers=True, text="points",
                      title="Evolución de Puntos y Goles vs Brecha de Campeón",
                      labels={"season": "Temporada", "points": "Puntos Obtenidos (UTD)"},
                      color_discrete_sequence=["#e3b341"])
    
    # Brecha de puntos
    fig_pts.add_trace(go.Bar(
        x=df["season"], y=df["gap"],
        name="Pts Perdidos vs Campeón",
        marker_color="#da3633",
        opacity=0.3
    ))
    
    # Diferencial de goles
    fig_pts.add_trace(go.Scatter(
        x=df["season"], y=df["gd"],
        name="Diferencial Goles (GD)",
        mode="lines+markers",
        line=dict(color="#2ea043", dash="dash")
    ))
    
    for idx, row in df[df["manager"] != df["manager"].shift(-1)].dropna().iterrows():
        if row["season"] != df["season"].iloc[-1]:
            # Plotly bug workaround: add_vline crashes on string categorical axes
            # Must strictly use add_shape primitive
            fig_pts.add_shape(
                type="line",
                x0=row["season"], x1=row["season"],
                y0=0, y1=1,
                xref="x", yref="paper",
                line=dict(color="#e3b341", dash="dot")
            )
            fig_pts.add_annotation(
                x=row["season"], y=0.95, yref="paper",
                text="⚠️ Despido/DT", showarrow=False,
                xanchor="left", yanchor="top",
                font=dict(size=10, color="#e3b341")
            )

    if trendline:
        z = sm.nonparametric.lowess(df["points"], range(len(df)), frac=0.3)
        fig_pts.add_trace(go.Scatter(x=df["season"], y=z[:,1], mode="lines",
                                     name="Tendencia (LOWESS)", line=dict(color="#58a6ff", width=2)))

    fig_pts.update_layout(**PLOTLY_THEME)
    return fig_pts

def graficar_eficiencia_dt(df_grp):
    fig_mgr = px.scatter(df_grp, x="avg_pos", y="ppg", size="seasons", color="manager_clean",
                         hover_name="manager_clean", hover_data=["pts_total", "total_comp"],
                         title="Eficiencia por Entrenador (PPG vs Posición Media)",
                         labels={"avg_pos": "Posición Promedio Interanual", "ppg": "PPG"},
                         color_discrete_sequence=px.colors.qualitative.Bold)
    
    fig_mgr.add_hline(y=1.7, line_dash="dash", line_color="#da3633", 
                      annotation_text="Zona de Riesgo (Top 4 imposible)", annotation_position="bottom right")
    fig_mgr.update_xaxes(autorange="reversed")
    fig_mgr.update_layout(**PLOTLY_THEME)
    return fig_mgr

def graficar_correlacion(df):
    cols_corr = ["points", "gf", "ga", "wins", "net_spend_m", "comp_fee_m"]
    corr = df[cols_corr].corr()
    fig_corr = go.Figure(data=go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.columns,
        colorscale="RdBu", zmin=-1, zmax=1,
        text=corr.values.round(2), texttemplate="%{text}", textfont={"size": 12}
    ))
    fig_corr.update_layout(**PLOTLY_THEME, title="Matriz de Correlación: Fricciones del Éxito", width=500, height=500)
    return fig_corr

def graficar_regresion_gf(df):
    fig_reg = px.scatter(df, x="gf", y="points", trendline="ols",
                         title="Regresión: Goles a Favor vs Puntos Reales",
                         labels={"gf": "Goles a Favor", "points": "Puntos Finales"},
                         color_discrete_sequence=["#2ea043"])
    fig_reg.update_layout(**PLOTLY_THEME)
    return fig_reg

def graficar_costo_por_punto(df_grp):
    # Sort to show highest cost first
    df_sorted = df_grp.sort_values("cost_per_point", ascending=True)
    fig_cost = px.bar(df_sorted, x="cost_per_point", y="manager_clean", orientation='h',
                      text="cost_per_point", color="cost_per_point",
                      color_continuous_scale="RdYlGn_r",
                      title="Auditoría de Capital: Costo por Punto Obtenido",
                      labels={"cost_per_point": "Costo de 1 Punto (£ Millones)", "manager_clean": "Director Técnico"})
    fig_cost.update_traces(texttemplate='£%{text}M', textposition='outside')
    fig_cost.update_layout(**PLOTLY_THEME, coloraxis_showscale=False)
    return fig_cost
