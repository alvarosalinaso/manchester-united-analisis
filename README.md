# Manchester United: What happened after Ferguson?

[![CI](https://github.com/alvarosalinaso/manchester-united-analisis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/manchester-united-analisis/actions/workflows/ci.yml) [![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org) [![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## What is this?

EN: Everyone has an opinion about Manchester United's decline. I wanted to quantify it. This project uses 32 seasons of Premier League data to measure the institutional instability, the gap with champions, and whether any manager actually got good results relative to the squad.

ES: Todos tienen una opinión sobre el declive del Manchester United. Yo quería cuantificarlo. Este proyecto usa 32 temporadas de Premier League para medir la inestabilidad institucional, la brecha con los campeones, y si algún entrenador realmente obtuvo buenos resultados relativos al plantel.

---

## Questions I asked

**P1 (Competitive gap):** How many points per season does United trail the champion by on average?

**P2 (Cost of instability):** How much has United spent on firing managers in severance packages?

**P3 (Manager efficiency):** Which manager got the most points per game relative to the squad available?

---

## How it works

```
data.py → load PL CSV data
analysis.py → KPIs, gap calculation, manager efficiency
causal_inference.py → Difference-in-Differences on managerial changes + placebo test
cohort_analysis.py → retention by manager era
```

### Key methods

- **Difference-in-Differences (DiD):** Estimates the causal effect of sacking a manager on subsequent performance, with placebo testing
- **Cohort analysis:** Player retention and squad stability across manager eras
- **OLS regression:** Relationship between managerial tenure and performance

---

## Key findings

| Metric | Value | What it means |
|--------|-------|---------------|
| Average gap to champion | ~20 pts/season | Consistently outside title race |
| Manager severance cost | ~£32M | Money spent firing people |
| Best manager (pts/game) | Mourinho (1.97) | Got most from available squad |
| Worst manager (pts/game) | Ten Hag (1.78) | Underperformed relative to investment |

The ~20 point gap is the difference between top-4 and mid-table — meaning repeated failure to qualify for Champions League revenue.

---

## Visualizations

<details>
<summary><strong>Datawrapper — PL Benchmark</strong></summary>

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;">
  <iframe src="https://datawrapper.dwcdn.net/vfOvM/" title="PL Benchmark" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" loading="lazy" allowfullscreen></iframe>
</div>
</details>

<details>
<summary><strong>Observable — Correlation analysis</strong></summary>

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;">
  <iframe src="https://observablehq.com/@alvarosalinaso/manutd-correlation" title="Spending vs Points" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" loading="lazy" allowfullscreen></iframe>
</div>
</details>

---

## How to run

```bash
git clone https://github.com/alvarosalinaso/manchester-united-analisis.git
cd manchester-united-analisis
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python src/causal_inference.py
python src/cohort_analysis.py
pytest
```

---

## Project structure

```
manchester-united-analisis/
├── src/manutd_analysis/     # Main package (data, analysis, plots)
├── src/causal_inference.py  # DiD + placebo test
├── src/cohort_analysis.py   # Retention by manager era
├── tests/                   # Unit tests
└── requirements.txt
```

---

> **Álvaro Salinas Ortiz**
> [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz) | [Portfolio](https://alvarosalinaso.github.io/portfolio-web/)
