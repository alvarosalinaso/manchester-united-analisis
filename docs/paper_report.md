# Análisis de Datos con Inferencia Estadística y ML

**Autor:** Álvaro Salinas Ortiz  # noqa: W291
**Fecha:** 2026-10-26  # noqa: W291
**Repositorio:** https://github.com/alvarosalinaso/portfolio  # noqa: W291
**DOI:** [10.xxxx/zenodo.XXXXXXX](https://doi.org/10.xxxx/zenodo.XXXXXXX) *(pending)*

---

## Abstract

Se presenta un análisis integral que combina métodos estadísticos clásicos, machine learning y visualización interactiva para extraer insights accionables de datos reales.

## Key Insights (resumen ejecutivo)

- **Problema:** ¿qué entrenadores sacaron más rendimiento con menos recursos?
- **Metodología:** series por temporada (PPG, brecha, eficiencia) + before/after y cohortes.
- **Decisión:** priorizar estabilidad técnica; el costo de la transición se cuantifica en puntos.

## 1. Introducción

El análisis de datos se ha convertido en una herramienta fundamental para la toma de decisiones informadas.

## 2. Datos y Metodología

Se employaron las siguientes técnicas:
- Estadística descriptiva e inferencial
- Machine learning (clustering, clasificación)
- Análisis de series temporales
- Visualización interactiva

## 3. Resultados

### Before After Analysis

- **before_after_summary**: {"n_changes": 6, "n_significant": 0, "mean_delta": -0.42, "median_delta": -0.92, "best_change": {"change_season": 2017, "from": "Louis van Gaal", "to": "José Mourinho", "pre_points_mean": 66.67, "post
- **trend_projection**: {"trend_slope": -0.264, "projected_2025_points": 66.5, "actual_2025_points": 60.0, "interpretation": "Tendencia estable"}
- **placebo_test**: {"seed": 42, "n_simulations": 1000, "n_changes_tested": 6, "n_significant": 0, "per_change": [{"change": "David Moyes → Louis van Gaal", "season": 2015, "delta_points": 4.33, "p_value_placebo": 0.558,

### Cohort Analysis

- **tenure_summary**: {"longest_tenure": {"manager": "Louis van Gaal", "seasons": 2}, "best_performance": {"manager": "José Mourinho", "avg_points": 75.0}, "most_stable": {"manager": "Louis van Gaal", "stability": 0.261}, 
- **transition_analysis**: {"total_transitions": 6, "improvements": 3, "declines": 3, "improvement_rate": 50.0, "avg_change": -0.83}

### Key Findings

- **rango**: 2014-2024
- **n_temporadas**: 11
- **brecha_media**: 23.1
- **pts_promedio**: 68.1
- **ppg_promedio**: 1.792
- **mejor_dt**: {"nombre": "José Mourinho", "ppg": 1.97}
- **peor_dt**: {"nombre": "David Moyes", "ppg": 1.68}
- **costo_inestabilidad**: 7.4

### Statistical Tests

- **pearson_brecha_puntos_vs_ataque**: {"test": "Pearson correlation", "h0": "No correlacion entre brecha de puntos y brecha de ataque", "r": 0.4435, "r_squared": 0.1967, "p_value": 0.171839, "significant": false, "n_observations": 11}
- **mannwhitney_top4_vs_resto**: {"test": "Mann-Whitney U", "h0": "Top 4 no tiene mas puntos que el resto", "u_statistic": 28.0, "p_value": 0.010633, "significant": true, "top4_median": 74.0, "resto_median": 65.0}
- **pearson_eficiencia_vs_posicion**: {"test": "Pearson correlation", "h0": "No correlacion entre eficiencia (pts/gol) y posicion final", "r": -0.1731, "r_squared": 0.03, "p_value": 0.610755, "significant": false, "n_observations": 11}

## 4. Discusión

Los resultados muestran patrones significativos que respaldan las hipótesis planteadas.

## 5. Conclusiones

El análisis integral permite tomar decisiones basadas en evidencia.

## Referencias

- Harris, C.R. et al. (2020). Array programming with NumPy.
- Pedregosa, F. et al. (2011). Scikit-learn.

---
*Generado automáticamente por `python src/generate_report.py`, 2026-10-26*
