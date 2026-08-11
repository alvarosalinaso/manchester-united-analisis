# Manchester United Performance Analysis (2014-2024)

[![CI](https://github.com/alvarosalinaso/manchester-united-analisis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/manchester-united-analisis/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Análisis detallado del rendimiento del Manchester United en la Premier League durante la década post-Ferguson (2014-2024). Cuantifica la brecha con el campeón, el costo de la inestabilidad técnica y la eficiencia por entrenador mediante dashboards interactivos.

## Tabla de contenidos

- [Dashboard en Vivo](#dashboard-en-vivo)
- [Hallazgos Clave](#hallazgos-clave)
- [Stack](#stack)
- [Arquitectura](#arquitectura)
- [Instalación](#instalación)
- [Inicio Rápido](#inicio-rápido)
- [Testing](#testing)
- [Contribución](#contribución)
- [Licencia](#licencia)

## Dashboard en Vivo

👉 **[manchester-united-analisis.streamlit.app](https://manchester-united-analisis.streamlit.app)** — *Se activa al desplegar en Streamlit Cloud.*

## Hallazgos Clave

- **Brecha promedio con el campeón**: ~20 puntos por temporada
- **Costo de inestabilidad**: ~£32M en compensaciones a entrenadores despedidos
- **Mejor DT por eficiencia**: Mourinho (1.86 pts/partido)
- **Peor DT**: Ten Hag (1.58 pts/partido)

## Stack

| Capa | Tecnología |
|------|-----------|
| **Lenguaje** | Python 3.9+ |
| **Data** | Pandas, NumPy |
| **Visualización** | Streamlit, Plotly, Matplotlib, Seaborn |
| **ML** | Scikit-learn (simulador predictivo) |
| **Testing** | Pytest, Pytest-cov |
| **Lint & Format** | Ruff |
| **CI/CD** | GitHub Actions (matrix 3.9–3.13) |
| **Empaquetado** | pyproject.toml |
| **Licencia** | MIT |

## Arquitectura

```
┌─────────────┐   ┌──────────────┐   ┌──────────────┐
│  data.py    │──▶│ analysis.py  │──▶│   plots.py   │
│ (carga/KPI) │   │ (métricas)   │   │ (visualiza)  │
└─────────────┘   └──────────────┘   └──────────────┘
      │                                        │
      └───────▶ app.py (Streamlit) ─────▶ Dashboard
```

- **data.py** — carga del CSV de Premier League, enriquecimiento y KPIs calculados.
- **analysis.py** — eficiencia por entrenador, estabilidad y costo de inestabilidad.
- **plots.py** — gráficos de brecha y rentabilidad ofensiva.
- **app.py** — capa de presentación (Streamlit) que orquesta los módulos.

## Estructura

```
manchester-united-analisis/
├── src/manutd_analysis/   # Paquete principal
│   ├── data.py            # Carga y limpieza
│   ├── analysis.py        # Métricas y modelos
│   └── plots.py           # Visualizaciones
├── tests/                 # Tests unitarios (Pytest)
├── .github/workflows/     # CI (lint + matrix de tests + coverage)
├── assets/figures/        # Gráficos generados
├── app.py                 # Dashboard Streamlit
├── pyproject.toml         # Configuración (build, ruff, pytest, coverage)
└── requirements.txt       # Dependencias de runtime
```

## Instalación

```bash
git clone https://github.com/alvarosalinaso/manchester-united-analisis.git
cd manchester-united-analisis
python -m venv .venv
# Windows: .venv\Scripts\activate   |  Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

Para desarrollo (incluye linters y tests):

```bash
pip install -e ".[dev]"
```

## Inicio Rápido

```bash
streamlit run app.py
```

```bash
python -c "from manutd_analysis.analysis import resumen_por_entrenador; print('OK')"  # Verificar instalación
```

## Testing

```bash
pytest                      # Tests + cobertura
ruff check .                # Lint
ruff format --check .       # Verificación de formato
```

## Contribución

Revisa [CONTRIBUTING.md](CONTRIBUTING.md) para convenciones de commits, estilo de código y flujo de PRs.

## Licencia

Distribuido bajo la licencia [MIT](LICENSE). Copyright © 2026 Álvaro Salinas.
