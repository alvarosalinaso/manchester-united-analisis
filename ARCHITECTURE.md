# Arquitectura, manchester-united-analisis

## Principios

1. **Una sola fuente de verdad.** Todo se deriva de `data/pl-tables-1993-2024.csv` y `data/passing_players_2425.csv`. `data/analisis_united_2014_2024.csv` y `data/export/` son artefactos que el pipeline regenera; nadie los edita a mano.
2. **Fail-fast.** `validator.py` detiene la ejecución ante columnas faltantes, valores no numéricos, temporadas sin cobertura o más de un campeón por temporada.
3. **Cálculo puro, E/S en los bordes.** `metrics.py`, `inference.py` y `cohorts.py` no leen ni escriben archivos. Solo `data_loader.py` (entrada) y `pipeline.py`/`exports.py`/`reporting.py` (salida) tocan disco.
4. **Sin rutas en duro.** `config.ProjectPaths` deriva las rutas de la raíz del repo, o de `MANUTD_ROOT`.
5. **Observabilidad.** `logging` en todos los módulos (nivel vía `MANUTD_LOG_LEVEL`). No hay `print()`.

## Flujo de datos

```
data/*.csv
   │  data_loader.load_pl_tables / load_passing   (pathlib, cabeceras saneadas, tipos estrictos)
   ▼
validator.validate_*                               (SchemaError ante cualquier desvío)
   ▼
metrics.build_season_kpis ──► metrics.* / inference.* / cohorts.*   (funciones puras)
   ▼
pipeline.write_outputs ──► data/export/*.json|csv, assets/, docs/paper_report.md
                      └──► reporting.sync_document → README.md, dashboard.html
app.py ──► pipeline.compute (mismo cálculo, en memoria, con caché de Streamlit)
```

## Módulos (`src/manutd_analysis/`)

| Módulo | Responsabilidad |
|--------|-----------------|
| `config.py` | `ProjectPaths`, constantes de dominio (temporadas, entrenadores, semilla placebo) |
| `logging_config.py` | `setup_logging()` único |
| `data_loader.py` | Lectura CSV con errores tipados (`DataLoadError`), saneamiento y casteo |
| `validator.py` | Contratos de esquema (`SchemaError`) |
| `metrics.py` | KPIs por temporada, PPG por entrenador, costo de la inestabilidad, benchmark, pases/90 |
| `inference.py` | Pearson, Welch, Mann-Whitney; pre/post por cambio de DT con test placebo |
| `cohorts.py` | Cohortes por entrenador y transiciones |
| `plots.py` | Figuras PNG |
| `exports.py` | CSV/JSON para Datawrapper, Flourish y Observable |
| `reporting.py` | Tablas Markdown/HTML, informe técnico, marcadores `<!-- FIND:x -->` |
| `pipeline.py` | `compute()` (en memoria), `run()` (con salidas) y CLI `python -m manutd_analysis` |

## Despliegue

- **Local:** `streamlit run app.py`.
- **Docker:** `docker build -t manutd . && docker run -p 8501:8501 manutd`.
- **Streamlit Community Cloud:** apuntar a `app.py`; usa `requirements.txt` y no requiere secretos.

## Calidad

- `pytest` con gate de cobertura del 85 % sobre el paquete; incluye una prueba de punta a punta que escribe en un directorio temporal y otra que verifica que el README publicado coincide con lo calculado.
- `ruff check` y `ruff format --check` en CI (Python 3.10 a 3.13).
