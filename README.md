# Analisis cuantitativo del rendimiento competitivo del Manchester United en la Premier League (2013-2024): Inestabilidad institucional, brecha de rendimiento y eficiencia de gestion

[![CI](https://github.com/alvarosalinaso/manchester-united-analisis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/manchester-united-analisis/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![Plotly.js](https://img.shields.io/badge/Plotly.js-3.x-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/javascript/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 1. Titulo Academico y Contexto Estrategico

Este estudio cuantifica la degradacion sistematica del rendimiento deportivo del Manchester United Football Club en la Premier League durante la decada post-Alex Ferguson (2013-2024). El problema central es la inestabilidad institucional cronica: siete entrenadores distintos en once temporadas, una brecha persistente con el club campeon, y un desembolso financiero significativo en compensaciones por terminacion anticipada de contratos. El analisis busca transformar datos de rendimiento deportivo en evidencia accionable para la toma de decisiones estrategicas en organizaciones de alto rendimiento.

## 2. Preguntas de Investigacion e Hipotesis

Formulamos tres preguntas cuantitativas centrales:

- **P1 (Brecha competitiva):** ¿Cual es la magnitud promedio de la brecha en puntos por temporada entre el Manchester United y el club campeon de la Premier League?
- **P2 (Costo de la inestabilidad):** ¿Cual es el costo financiero acumulado de las compensaciones a entrenadores despedidos durante el periodo de analisis?
- **P3 (Eficiencia de gestion):** ¿Que entrenador logro la mayor eficiencia en la obtencion de puntos por partido gestionado?

**Hipotesis operacionales:** La inestabilidad tecnica correlaciona negativamente con la obtencion de titulos, generando un costo financiero y competitivo medible. El entrenador con mayor ratio puntos/partido representa la gestion mas eficiente dentro del conjunto de datos.

## 3. Pipeline Metodologico y Arquitectura de Datos

El pipeline metodologico se estructura en cuatro fases secuenciales, codificadas en Python y validadas mediante pruebas automatizadas.

```
┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
│   FASE 1: CARGA     │──▶│  FASE 2: KPIs        │──▶│  FASE 3: ANALISIS    │
│   data.py            │   │  (calculo)            │   │  econometrico        │
│   (ETL CSV PL)       │   │                       │   │  analysis.py         │
└──────────────────────┘   └──────────────────────┘   └──────────────────────┘
         │                                                    │
         ▼                                                    ▼
┌──────────────────────┐                         ┌──────────────────────┐
│  FASE 4: SIMULACION │◀────────────────────────│  EXPORTACION JSON    │
│  Scikit-learn        │                         │  (consumo frontend)  │
│  (modelo predictivo) │                         │                      │
└──────────────────────┘                         └──────────────────────┘
```

- **Fase 1 (data.py):** Carga y normalizacion de datos CSV de la Premier League. Limpieza, transformacion de tipos y enriquecimiento con metricas derivadas.
- **Fase 2 (KPIs):** Calculo de indicadores clave: puntos por temporada, brecha con el campeon, puntos por partido por entrenador, y costo acumulado de compensaciones.
- **Fase 3 (analysis.py):** Analisis econométrico: regresion de brecha, correlacion entre estabilidad tecnica y rendimiento, y eficiencia relativa por manager.
- **Fase 4 (Simulacion):** Implementacion de modelo predictivo con Scikit-learn para proyectar escenarios de rendimiento bajo distintas politicas de gestion.

## 4. Hallazgos Clave y Business/Domain Insights

Los resultados empiricos revelan patrones criticos para la comprension del deterioro competitivo:

| Metrica | Valor | Implicacion Estrategica |
|---------|-------|-------------------------|
| **Brecha promedio con el campeon** | ~20 puntos por temporada | El club opera sistemáticamente por debajo del umbral de competencia por el titulo. |
| **Costo de inestabilidad** | ~£32M en compensaciones | Desembolso financiero directo sin retorno deportivo proporcional. |
| **Mejor DT por eficiencia** | Mourinho (1.97 pts/partido) | Maximizacion del rendimiento relativo al talento disponible. |
| **Peor DT por eficiencia** | Ten Hag (1.78 pts/partido) | Suboptimalidad en la gestion del plantel y estrategia competitiva. |

**Insight econométrico:** La brecha de ~20 puntos equivale a la diferencia entre un top-4 y un equipo de mitad de tabla, lo que implica una perdida recurrente de calificacion a competiciones europeas de elite y sus ingresos asociados.

## 5. Dashboard y Visualizaciones Interactivas

El analisis se materializa en tres plataformas de visualizacion interactivas, cada una optimizada para un tipo de insight especifico.

### 5.1 Benchmark de la Premier League (Datawrapper)

Comparativa longitudinal del rendimiento del Manchester United contra el promedio del top-6 y el campeon.

<div style="width: 100%; max-width: 800px; margin: 0 auto;">
  <iframe src="https://datawrapper.dwcdn.net/XXXXXXXX/" width="100%" height="400" frameborder="0" style="border: none;" loading="lazy"></iframe>
  <p style="text-align: center; font-size: 0.85em; color: #666;">Figura 1: Evolucion de puntos por temporada (2013-2024)</p>
</div>

### 5.2 Red de Relaciones Entrenador-Equipo (Flourish)

Grafo de relaciones que visualiza la red de conexiones entre entrenadores, jugadores clave y metricas de rendimiento.

<div style="width: 100%; max-width: 800px; margin: 0 auto;">
  <iframe src="https://flo.uri.sh/story/XXXXXXXX/embed" width="100%" height="600" frameborder="0" style="border: none;" loading="lazy"></iframe>
  <p style="text-align: center; font-size: 0.85em; color: #666;">Figura 2: Red de influencia y rendimiento por gestion</p>
</div>

### 5.3 Matriz de Correlacion (Observable)

Analisis de correlacion entre variables clave: puntos, gol differential, gasto en fichajes y estabilidad tecnica.

<div style="width: 100%; max-width: 800px; margin: 0 auto;">
  <iframe src="https://observablehq.com/embed/XXXXXXXX" width="100%" height="500" frameborder="0" style="border: none;" loading="lazy"></iframe>
  <p style="text-align: center; font-size: 0.85em; color: #666;">Figura 3: Matriz de correlacion de variables de rendimiento</p>
</div>

**Dashboard integrado completo:** [Portfolio Web](https://alvarosalinaso.github.io/portfolio-web/) con tabs dedicados a metricas historicas, analisis por entrenador, diagnostico financiero y simulador predictivo.

## 6. Reproducibilidad y Entorno Tecnico

Este estudio esta disenado para ser completamente reproducible. El entorno tecnico y los comandos exactos se documentan a continuacion.

### Entorno de Desarrollo

| Componente | Especificacion |
|------------|----------------|
| **Lenguaje** | Python 3.9+ |
| **Frontend** | JavaScript/Plotly.js (desplegado en GitHub Pages) |
| **Data** | Pandas, NumPy, SciPy |
| **ML** | Scikit-learn (simulador predictivo) |
| **Testing** | Pytest, Pytest-cov |
| **Lint** | Ruff |
| **CI/CD** | GitHub Actions (matrix 3.9-3.13) |
| **Licencia** | MIT |

### Comandos de Reproduccion

```bash
# Clonar repositorio
git clone https://github.com/alvarosalinaso/manchester-united-analisis.git
cd manchester-united-analisis

# Crear entorno virtual
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
# Para desarrollo (linters, tests)
pip install -e ".[dev]"

# Ejecutar tests con cobertura
pytest

# Verificar calidad de codigo
ruff check .
ruff format --check .

# Generar datos para visualizaciones
python -c "
from manutd_analysis.data import load_data
from manutd_analysis.analysis import manager_summary
import json
df = load_data()
mgr = manager_summary(df)
data = {'seasons': df.to_dict('records'), 'manager_summary': mgr.to_dict('records')}
with open('../portfolio-web/public/data/manchester-united.json', 'w') as f:
    json.dump(data, f, indent=2)
"
```

### Estructura del Repositorio

```
manchester-united-analisis/
├── src/manutd_analysis/   # Paquete principal
│   ├── data.py            # Carga y limpieza
│   ├── analysis.py        # Metricas y modelos
│   └── plots.py           # Visualizaciones
├── tests/                 # Tests unitarios (Pytest)
├── .github/workflows/     # CI (lint + matrix de tests + coverage)
├── assets/figures/        # Graficos generados
├── pyproject.toml         # Configuracion (build, ruff, pytest, coverage)
└── requirements.txt       # Dependencias de runtime
```

Distribuido bajo la licencia MIT. Copyright 2026 Alvaro Salinas.