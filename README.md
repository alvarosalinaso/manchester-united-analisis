# Manchester United: Auditoría de Rendimiento (2014-2024)

Números crudos sobre el rendimiento post-Ferguson. Acá se ve matemáticamente cuánto cuesta echar entrenadores a mitad de temporada y la falta de rumbo deportivo.

## 📊 Objetivo
Evidenciar con datos financieros y deportivos (PPG, Costo por Punto) el nivel de inestabilidad del club en la última década.

## 🛠️ Stack
- Python 3.8+
- Pandas / Seaborn
- Pytest

## 📁 Repo
```
manchester-united-analisis/
├── src/ # scripts
├── tests/ # unit tests
├── assets/ # img resultantes
└── pyproject.toml
```

## Setup Rapido

1. `pip install -e .`
2. `pytest`
3. Para correr el scraper/analisis base:
    ```python
    from manutd_analysis.data import load_raw_data
    from manutd_analysis.plots import plot_efficiency
    
    df = load_raw_data()
    plot_efficiency(df)
    ```

## 📈 Hard Facts
- **La Brecha**: El equipo promedia ~20 puntos menos que el campeón de turno. 
- **Costo Hundido**: Tirar a un DT a la basura en medio del torneo destroza los puntos finales.
- **Mourinho & Van Gaal**: Estadísticamente los únicos que armaron un sistema eficiente de puntos/gol, pese al odio mediático.

> Creado por Álvaro Salinas Ortiz (alvarosalinasortiz@gmail.com)
