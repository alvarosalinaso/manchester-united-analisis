# Arquitectura — manchester-united-analisis

## Visión general
Análisis de rendimiento del Manchester United (2014-2024). Datos de Premier League, series temporales por entrenador, comparación descriptiva before/after, cohort analysis, visualizaciones matplotlib/seaborn.

## Componentes principales

### Datos
- `pl-tables-1993-2024.csv` — Tablas históricas Premier League
- `analisis_united_2014_2024.csv` — Dataset filtrado United
- `dw_benchmark_pl.csv` — Benchmarks
- `flourish_bump_manager.csv` — Datos para bump charts
- `observable_correlacion.csv` — Correlaciones

### Código (src/manutd_analysis/)
- `data.py`:
  - `cargar_y_filtrar_datos()`: PL tables → df United + KPIs (brecha_puntos, ppg, pts_por_gol)
  - `ENTRENADORES` — Dict año→entrenador
  - `_resolver_ruta()` — Path resolution
- `plots.py`:
  - `graficar_eficiencia_y_brecha()` — Scatter eficiencia vs brecha
  - `graficar_ppg_historico()` — Serie temporal PPG
  - `graficar_rentabilidad_ofensiva()` — GF/GA vs puntos
- `causal_inference.py` — run_causal_analysis (before/after descriptivo, no causal)
- `cohort_analysis.py` — run_cohort_analysis
- `statistical_tests.py` — run_statistical_tests
- `generate_tables.py` — generate
- `generate_report.py` — generate_report

### Notebook
- `analisis_united.ipynb` — Análisis exploratorio + visualizaciones

### Scripts
- `main.py` — Entry point

## Flujo de datos
```
pl-tables-1993-2024.csv → data.cargar_y_filtrar_datos → df United
df United → plots / causal_inference / cohort_analysis → gráficos + métricas
```

## Despliegue
- Docker: `Dockerfile` (Python 3.11)
- No es dashboard web — genera PNGs y reportes

## Tests
- `tests/test_data.py` — cargar_y_filtrar_datos, _resolver_ruta, ENTRENADORES
- `tests/test_plots.py` — graficar_* con matplotlib Agg backend
- `tests/test_analysis.py` — Smoke tests
- CI: pytest + coverage + ruff (Python 3.9, 3.11, 3.12, 3.13)
- pyproject.toml con optional-dependencies dev

## Estructura de paquete
- `src/manutd_analysis/` — Paquete instalable (`pip install -e .`)
- `pyproject.toml` — Configuración completa (build, ruff, pytest)