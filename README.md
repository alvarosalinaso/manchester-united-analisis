[![CI](https://github.com/alvarosalinaso/manchester-united-analisis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/manchester-united-analisis/actions/workflows/ci.yml)

# Manchester United: Auditoría de "Plata Quemada"

Análisis duro transversal y financiero del desgaste deportivo del Manchester United (Post-Ferguson). Esto no es sobre goles en contra, esto es sobre cuánto dinero le costó a INEOS/Glazers cada punto obtenido por cada entrenador que pasó por la banca.

## El Pipeline y el Dashboard
El repositorio expone una herramienta visual cruda para gerencia. Las métricas claves:
- **Net Spend per Point (Costo por Punto):** La división pura entre la inyección de libras esterlinas al mercado de fichajes y el rendimiento real final en la tabla.
- **Táctica vs Ruleta:** Mapas LOWESS de correlación que comprueban que comer goles no te hunde tanto financieramente como no meterlos. 
- **Bugfixes:** 
  - Código purgado de estructuras redundantes. 
  - Errores silenciados (`try-catch` genéricos en Plotly) totalmente removidos bajo la filosofía de "Fail-Fast".
  - Refactorización de rutas usando `pathlib` asegurando despliegues de entorno agnósticos (sin importar desde qué carpeta corras la aplicación, siempre levanta).

## Setup Local
Este proyecto levanta al vuelo usando Python vainilla. Solamente requiere instalar las dependencias visuales de `streamlit` y `plotly`.

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Despliégalo, lee los números y fíjate por qué la directiva prefiere mantener contratos de riesgo bajo antes que cortar de raíz y pagar compensaciones (Comp Fee = $32M enterrados en técnicos despedidos).

> Álvaro Salinas Ortiz | alvarosalinasortiz@gmail.com | [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz)
