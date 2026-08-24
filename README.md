# Manchester United Performance Analysis (2013-2024)

[![CI](https://github.com/alvarosalinaso/manchester-united-analisis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/manchester-united-analisis/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![Plotly.js](https://img.shields.io/badge/Plotly.js-3.x-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/javascript/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Análisis detallado del rendimiento del Manchester United en la Premier League durante la década post-Ferguson (2013-2024). Cuantifica la brecha con el campeón, el costo de la inestabilidad técnica y la eficiencia por entrenador mediante dashboards interactivos.

## Tabla de contenidos

- [Dashboard Integrado](#dashboard-integrado)
- [Hallazgos Clave](#hallazgos-clave)
- [Stack](#stack)
- [Arquitectura](#arquitectura)
- [Instalación](#instalación)
- [Inicio Rápido](#inicio-rápido)
- [Testing](#testing)
- [Contribución](#contribución)
- [Licencia](#licencia)

## Dashboard Integrado

👉 **Integrado en [Portfolio Web](https://alvarosalinaso.github.io/portfolio-web/)** → Tabs:
- **"⚽ Manchester United Performance"**: 4 tabs (Histórico, Entrenadores, Diagnóstico, Simulador)
- **"📊 Auditoría Financiera M. United"**: Simulador ROI por DT
- **"🕸️ Red de Pases United"**: Análisis de redes complejas (xT, betweenness, benchmark PL)

Desplegado en GitHub Pages (estático, sin backend Python).

## Hallazgos Clave

- **Brecha promedio con el campeón**: ~20 puntos por temporada
- **Costo de inestabilidad**: ~£32M en compensaciones a entrenadores despedidos
- **Mejor DT por eficiencia**: Mourinho (1.97 pts/partido)
- **Peor DT**: Ten Hag (1.78 pts/partido)

## Stack

| Capa | Tecnología |
|------|-----------|
| **Lenguaje** | Python 3.9+ (ETL/Análisis) · JavaScript/Plotly.js (Frontend) |
| **Data** | Pandas, NumPy, SciPy |
| **Visualización** | **Plotly.js** (integrado en Portfolio Web), Matplotlib, Seaborn |
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
      └────────────────▶ JSON export ──────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  portfolio-web/src/    │
              │  data/manchester-      │
              │  united.json           │
              └────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  Plotly.js charts      │
              │  (Vanilla JS modules)  │
              └────────────────────────┘
```

- **data.py** — carga del CSV de Premier League, enriquecimiento y KPIs calculados.
- **analysis.py** — eficiencia por entrenador, estabilidad y costo de inestabilidad.
- **plots.py** — gráficos de brecha y rentabilidad ofensiva.
- **JSON export** — datos serializados para consumo en Portfolio Web (Plotly.js).

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

## Generar datos para Portfolio Web

```bash
python -c "
from manutd_analysis.data import load_data
from manutd_analysis.analysis import manager_summary
import json, pandas as pd
df = load_data()
mgr = manager_summary(df)
data = {'seasons': df.to_dict('records'), 'manager_summary': mgr.to_dict('records')}
with open('../portfolio-web/public/data/manchester-united.json', 'w') as f:
    json.dump(data, f, indent=2)
print('Exported to portfolio-web')
"
```

## Ver Dashboard Interactivo

**[https://alvarosalinaso.github.io/portfolio-web/](https://alvarosalinaso.github.io/portfolio-web/)** → Tabs "⚽ Manchester United Performance" y "📊 Auditoría Financiera M. United"

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