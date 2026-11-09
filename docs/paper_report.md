# Manchester United 2014-2024: costo de la inestabilidad técnica

**Autor:** Álvaro Salinas Ortiz · **Generado:** 2026-11-09 · **Repositorio:** https://github.com/alvarosalinaso/manchester-united-analisis

## Resumen ejecutivo

- En 11 temporadas (2014-2024) el United terminó en promedio **23.1 puntos** detrás del campeón (rango 12–35).
- Las 2 temporadas con relevo de entrenador rindieron **~7.4 puntos menos** que las temporadas con un único DT.
- PPG por entrenador (temporadas completas): máximo José Mourinho (1.97), mínimo David Moyes (1.68).

## Datos y método

- Fuente: tablas finales de la Premier League 1993-2024 (20 equipos por temporada).
- Pipeline: ingesta tipada → validación de esquema fail-fast → métricas puras → exportación.
- Contrastes: Pearson, Welch y Mann-Whitney (α = 0.05); comparación pre/post de cada cambio de DT con test placebo de cortes aleatorios (semilla fija).

## Contrastes estadísticos

| Test | Estadístico | p-valor | Significativo |
|------|-------------|---------|---------------|
| pearson_brecha_puntos_vs_ataque | r=0.4435 | 0.1718 | no |
| mannwhitney_top4_vs_resto | u_statistic=28.0 | 0.0106 | sí |
| pearson_eficiencia_vs_posicion | r=-0.1731 | 0.6108 | no |

## Cambios de entrenador (pre/post, descriptivo)

| Cambio | Temporada | Δ pts (3 temp. post − pre) | p placebo |
|--------|-----------|-----------------------------|-----------|
| David Moyes → Louis van Gaal | 2015 | +4.3 | 0.558 |
| Louis van Gaal → José Mourinho | 2017 | +5.3 | 0.220 |
| José Mourinho → Mourinho / Solskjær | 2019 | -3.3 | 0.687 |
| Mourinho / Solskjær → Ole Gunnar Solskjær | 2020 | -6.0 | 0.109 |
| Ole Gunnar Solskjær → Solskjær / Rangnick | 2022 | -4.3 | 0.558 |
| Solskjær / Rangnick → Erik ten Hag | 2023 | +1.5 | 1.000 |

> Δ pre/post de cada cambio comparado contra 1000 cortes aleatorios (semilla 42), descriptivo, no causal.

## Cohortes por entrenador

- 7 cohortes (incluye temporadas compartidas); tenencia media 1.6 temporadas; rotación 6.36 entrenadores por cada 10 temporadas.
- Mayor tenencia: Louis van Gaal (2 temporadas).

## Limitaciones

- La comparación pre/post no identifica efectos causales (sin grupo control).
- No se modela gasto en fichajes ni valor de plantilla (sin fuente fiable).

---
*Generado automáticamente por `python -m manutd_analysis`.*
