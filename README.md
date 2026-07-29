# Manchester United Performance Analysis (2014-2024)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Análisis detallado del rendimiento del Manchester United en la Premier League durante la década post-Ferguson (2014-2024). Cuantifica la brecha con el campeón, el costo de la inestabilidad técnica y la eficiencia por entrenador mediante dashboards interactivos.

## Dashboard en Vivo

👉 **[manchester-united-analisis.streamlit.app](https://manchester-united-analisis.streamlit.app)**

## Hallazgos Clave

- **Brecha promedio con el campeón**: ~20 puntos por temporada
- **Costo de inestabilidad**: ~£32M en compensaciones a entrenadores despedidos
- **Mejor DT por eficiencia**: Mourinho (1.86 pts/partido)
- **Peor DT**: Ten Hag (1.58 pts/partido)

## Stack

| Capa | Tecnología |
|------|-----------|
| **Lenguaje** | Python 3.8+ |
| **Data** | Pandas, NumPy |
| **Visualización** | Streamlit, Plotly, Matplotlib, Seaborn |
| **ML** | Scikit-learn (simulador predictivo) |
| **Testing** | Pytest |
| **Empaquetado** | pyproject.toml |

## Estructura

```
manchester-united-analisis/
├── src/manutd_analysis/   # Paquete principal
│   ├── data.py            # Carga y limpieza
│   ├── analysis.py        # Métricas y modelos
│   └── plots.py           # Visualizaciones
├── tests/                 # Tests unitarios (Pytest)
├── assets/figures/        # Gráficos generados
├── app.py                 # Dashboard Streamlit
├── pyproject.toml         # Configuración del proyecto
└── requirements.txt       # Dependencias
```

## Inicio Rápido

```bash
pip install -r requirements.txt
streamlit run app.py
```

```bash
pytest                           # Tests
python -c "from manutd_analysis.analysis import metricas_entrenadores; print('OK')"  # Verificar instalación
```

## Contacto

**Álvaro Salinas Ortiz** — [LinkedIn](https://linkedin.com/in/alvaro-salinas-ortiz) · 
