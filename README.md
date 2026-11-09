# United Performance Intelligence: costo de la inestabilidad técnica (2014-2024)

[![CI](https://github.com/alvarosalinaso/manchester-united-analisis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/manchester-united-analisis/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Streamlit](https://img.shields.io/badge/App-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](app.py)
[![Estado](https://img.shields.io/badge/estado-producción-2ea44f)](#reproducibilidad-en-4-pasos)
[![Licencia](https://img.shields.io/badge/licencia-MIT-green)](LICENSE)

Pipeline analítico que convierte 32 años de tablas finales de la Premier League en un diagnóstico cuantitativo: cuántos puntos pierde una organización deportiva de élite cuando rota su liderazgo técnico, y dónde está realmente la brecha con el campeón.

---

## Contexto del problema operativo

Entre 2014 y 2024 el Manchester United tuvo **5 entrenadores titulares, 2 temporadas con relevo a mitad de curso y 0 títulos de liga**, con uno de los mayores presupuestos del fútbol mundial. El debate sobre las causas se apoya en opiniones; la directiva no tenía una métrica comparable que separara tres hipótesis:

1. **Rendimiento del entrenador:** ¿algún DT rindió de forma claramente superior por partido?
2. **Costo de la rotación:** ¿cuánto rendimiento se pierde en la temporada en que se cambia al DT?
3. **Brecha estructural:** ¿el problema es la liga o la distancia con la élite?

Es el mismo problema que enfrenta cualquier operación con alta rotación en cargos de liderazgo: el costo de la transición es real, pero no se ve si no se mide de forma sistemática. Este sistema lo mide con una única fuente de verdad, validación automática de los datos y resultados reproducibles.

---

## Hallazgos clave y métricas de impacto

Las tablas se regeneran automáticamente desde los datos (`python -m manutd_analysis`).

<!-- FIND:table -->| Métrica | Valor | Lectura de negocio |
|---------|-------|--------------------|
| Brecha media vs campeón (2014-2024) | **23.1 pts/temporada** | Rango 12–35 pts; ninguna temporada en disputa real del título |
| PPG United vs PPG campeón | 1.79 vs 2.40 | Diferencia estructural, no coyuntural |
| Mejor entrenador (PPG) | José Mourinho (1.97) | Máximo rendimiento por partido en temporadas completas |
| Peor entrenador (PPG) | David Moyes (1.68) | Mínimo del período |
| Costo de la inestabilidad | **~7.4 pts** | Puntos perdidos en cada temporada con relevo de DT (2 casos) |
| Temporadas en Top 4 | 5 de 11 | Acceso a Champions League no garantizado |
| Ventaja PPG vs media PL (sin United) | +0.43 | Sigue sobre la media de la liga: el problema es la élite, no la liga |<!-- /FIND:table -->

### Estabilidad frente a relevo de entrenador

<!-- FIND:stability -->| Escenario | Pts/temporada | PPG | Goles a favor | Brecha vs campeón |
|-----------|---------------|-----|---------------|-------------------|
| Estable (1 Técnico) | 69.4 | 1.83 | 61.2 | 20.8 |
| Transición (Relevo) | 62.0 | 1.63 | 61.0 | 33.5 |<!-- /FIND:stability -->

Una temporada con relevo de DT cuesta **~<!-- FIND:costo -->7.4<!-- /FIND:costo --> puntos** y en ese grupo está la peor brecha del período (2022). Es una diferencia del mismo orden que la que separa las temporadas del United dentro y fuera del Top 4 (Mann-Whitney significativo, ver `data/export/statistical_tests.json`), es decir, la línea entre entrar o no a la Champions League.

### Rendimiento por entrenador

<!-- FIND:managers -->| Entrenador | Temporadas | Pts/temporada | Posición media | PPG | Brecha vs campeón |
|------------|------------|---------------|----------------|-----|-------------------|
| José Mourinho | 2 | 75.0 | 4.0 | 1.97 | 21.5 |
| Ole Gunnar Solskjær | 2 | 70.0 | 2.5 | 1.84 | 22.5 |
| Louis van Gaal | 2 | 68.0 | 4.5 | 1.79 | 16.0 |
| Erik ten Hag | 2 | 67.5 | 5.5 | 1.78 | 22.5 |
| Mourinho / Solskjær | 1 | 66.0 | 6.0 | 1.74 | 32.0 |
| David Moyes | 1 | 64.0 | 7.0 | 1.68 | 22.0 |
| Solskjær / Rangnick | 1 | 58.0 | 6.0 | 1.53 | 35.0 |<!-- /FIND:managers -->

### Benchmark frente al resto de la liga

<!-- FIND:bench -->| Temporada | PPG United | PPG media PL (sin United) | Δ PPG |
|-----------|------------|---------------------------|-------|
| 2014 | 1.68 | 1.38 | +0.30 |
| 2015 | 1.84 | 1.35 | +0.49 |
| 2016 | 1.74 | 1.34 | +0.40 |
| 2017 | 1.82 | 1.37 | +0.45 |
| 2018 | 2.13 | 1.33 | +0.80 |
| 2019 | 1.74 | 1.39 | +0.35 |
| 2020 | 1.74 | 1.36 | +0.38 |
| 2021 | 1.95 | 1.36 | +0.59 |
| 2022 | 1.53 | 1.38 | +0.15 |
| 2023 | 1.97 | 1.35 | +0.62 |
| 2024 | 1.58 | 1.37 | +0.21 |<!-- /FIND:bench -->

**Lectura de negocio:** el United supera a la media de la liga en las 11 temporadas, pero queda en promedio **<!-- FIND:brecha -->23.1<!-- /FIND:brecha --> puntos** detrás del campeón. El déficit no es de competitividad general. Es una brecha de élite que ningún cambio de entrenador cerró: ninguno de los 6 cambios supera el test placebo de 1.000 cortes aleatorios (ver `docs/paper_report.md`).

<details>
<summary><strong>Pases por 90 minutos, plantel 2024-25 (mín. 900 minutos)</strong></summary>

<!-- FIND:passing -->| Jugador | Pos | 90s | PrgP/90 | KP/90 | Pctl PrgP (plantel) | Pctl KP (plantel) |
|---------|-----|-----|---------|-------|---------------------|-------------------|
| Bruno Fernandes | MF | 54.7 | 8.46 | 2.47 | 100 | 100 |
| Lisandro Martínez | DF | 30.0 | 6.13 | 0.53 | 95 | 38 |
| Casemiro | MF | 31.1 | 5.05 | 1.16 | 90 | 81 |
| Mason Mount | MF | 10.8 | 4.35 | 0.83 | 86 | 52 |
| Christian Eriksen | MF | 19.3 | 3.99 | 2.44 | 81 | 95 |
| Noussair Mazraoui | DF | 49.8 | 3.86 | 0.58 | 76 | 43 |
| Diogo Dalot | DF | 49.5 | 3.47 | 0.87 | 71 | 60 |
| Leny Yoro | DF | 22.8 | 3.25 | 0.22 | 64 | 17 |
| Patrick Dorgu | DF | 16.9 | 3.25 | 1.07 | 64 | 71 |
| Kobbie Mainoo | MF | 23.0 | 3.17 | 0.87 | 57 | 60 |
| Victor Lindelöf | DF | 13.7 | 2.85 | 0.22 | 52 | 17 |
| Amad Diallo | MF,FW | 30.6 | 2.55 | 1.99 | 48 | 90 |
| Joshua Zirkzee | FW,MF | 25.2 | 2.54 | 0.75 | 43 | 48 |
| Manuel Ugarte | MF | 32.0 | 2.47 | 0.47 | 38 | 33 |
| Harry Maguire | DF | 30.9 | 2.36 | 0.42 | 33 | 29 |
| Matthijs de Ligt | DF | 34.6 | 2.17 | 0.23 | 29 | 24 |
| Marcus Rashford | FW,MF | 16.6 | 2.05 | 1.08 | 24 | 76 |
| Alejandro Garnacho | MF,FW | 39.7 | 1.96 | 1.49 | 19 | 86 |
| Rasmus Højlund | FW | 36.8 | 0.87 | 0.95 | 14 | 67 |
| André Onana | GK | 50.7 | 0.08 | 0.02 | 10 | 10 |
| Altay Bayındır | GK | 10.3 | 0.00 | 0.00 | 5 | 5 |<!-- /FIND:passing -->

Percentiles internos del plantel. Fuente: FBref (Opta).
</details>

**Alcance.** La comparación pre/post de cada cambio es descriptiva y no causal (no hay grupo de control). No se modelan el gasto en fichajes ni el valor de la plantilla, porque no hay una fuente verificable.

---

## Arquitectura del sistema

```
manchester-united-analisis/
├── app.py                         # Dashboard interactivo (Streamlit + Plotly), sin consola
├── main.py                        # Atajo: equivale a `python -m manutd_analysis`
├── src/manutd_analysis/
│   ├── config.py                  # Rutas derivadas de la raíz (o MANUTD_ROOT) y constantes de dominio
│   ├── logging_config.py          # Logging centralizado; nivel vía MANUTD_LOG_LEVEL
│   ├── data_loader.py             # Ingesta: pathlib, saneamiento de cabeceras, casteo estricto de tipos
│   ├── validator.py               # Validación fail-fast: columnas, nulos, cobertura de temporadas, campeón único
│   ├── metrics.py                 # Funciones puras: KPIs, benchmark, pases/90; división segura (0 → NaN)
│   ├── inference.py               # Pearson, Welch, Mann-Whitney; pre/post con test placebo (semilla fija)
│   ├── cohorts.py                 # Cohortes por entrenador: tenencia, estabilidad, transiciones
│   ├── plots.py                   # Figuras estáticas (matplotlib/seaborn)
│   ├── exports.py                 # CSV/JSON para Datawrapper, Flourish y Observable
│   ├── reporting.py               # Tablas Markdown/HTML, informe técnico, sincronización del README
│   └── pipeline.py                # Orquestador y CLI: ingesta → validación → métricas → salidas
├── data/
│   ├── pl-tables-1993-2024.csv    # Fuente: tablas finales PL (20 equipos por temporada)
│   ├── passing_players_2425.csv   # Fuente: exportación FBref, plantel United 2024-25
│   ├── analisis_united_2014_2024.csv  # Derivado: lo regenera el pipeline
│   └── export/                    # Derivados: JSON de inferencia, CSV de benchmark y para embeds
├── docs/paper_report.md           # Informe técnico generado
├── assets/                        # Figuras PNG y tabla ejecutiva HTML generadas
└── tests/                         # pytest: unitarios por módulo + prueba de punta a punta
```

**Flujo:** `data_loader` lee y tipa → `validator` corta la ejecución ante cualquier desviación del esquema → `metrics`, `inference` y `cohorts` calculan sin efectos secundarios → `pipeline` escribe los artefactos y reinyecta las cifras en este README y en `dashboard.html`. Un test verifica que las cifras publicadas coincidan con las calculadas.

**Datos y licencia:** los datos de FBref pertenecen a sus proveedores (Opta) y se usan citando la fuente. No están cubiertos por la licencia MIT, que aplica solo al código.

---

## Reproducibilidad en 4 pasos

**1. Clonar**
```bash
git clone https://github.com/alvarosalinaso/manchester-united-analisis.git && cd manchester-united-analisis
```

**2. Crear el entorno virtual** (en Windows, actívalo con `.venv\Scripts\activate`)
```bash
python -m venv .venv && source .venv/bin/activate
```

**3. Instalar dependencias**
```bash
pip install -r requirements.txt && pip install -e . --no-deps
```

**4. Ejecutar**
```bash
python -m manutd_analysis          # pipeline completo: exports, informe, figuras y README
streamlit run app.py               # dashboard interactivo en http://localhost:8501
```

Para desarrollo: `pip install -r requirements-dev.txt` y luego `pytest` (incluye un gate de cobertura) y `ruff check .`.

---

## Perfil del autor

**Álvaro Salinas Ortiz**, Analista de Datos y Operaciones · Business Analytics

Traduzco problemas operativos en métricas accionables: diseño pipelines de datos validados de punta a punta, cuantifico el impacto de decisiones de gestión y entrego resultados que otros pueden reproducir y auditar.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-alvaro--salinas--ortiz-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/alvaro-salinas-ortiz)
[![GitHub](https://img.shields.io/badge/GitHub-alvarosalinaso-181717?logo=github&logoColor=white)](https://github.com/alvarosalinaso)
[![Portfolio](https://img.shields.io/badge/Portfolio-web-555?logo=googlechrome&logoColor=white)](https://alvarosalinaso.github.io/portfolio-web/)
