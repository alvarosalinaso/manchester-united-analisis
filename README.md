[![CI](https://github.com/alvarosalinaso/manchester-united-analisis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/manchester-united-analisis/actions/workflows/ci.yml)

# Manchester United: Auditoría de Dinero Perdido

Análisis duro transversal y financiero del desgaste deportivo del Manchester United (Post-Ferguson). Esto no es sobre goles en contra, esto es sobre cuánto dinero le costó a los dueños cada punto obtenido por cada entrenador que pasó por el banquillo.

## El Flujo de Datos y el Panel Visual
El repositorio expone una herramienta visual cruda para gerencia. Las métricas claves:
- **Gasto Neto por Punto:** La división pura entre la inyección de libras esterlinas al mercado de fichajes y el rendimiento real final en la tabla de posiciones.
- **Táctica contra Azar:** Mapas de correlación que comprueban que recibir goles no te hunde tanto financieramente como no anotarlos. 
- **Correcciones Recientes:** 
  - Código purgado de estructuras redundantes. 
  - Errores silenciados (excepciones genéricas) totalmente removidos bajo la filosofía de "Falla Rápida".
  - Refactorización de rutas asegurando despliegues estables sin importar desde qué carpeta ejecutes la aplicación.

## Configuración Inicial
Este proyecto inicia rápidamente usando Python. Solamente requiere instalar las dependencias visuales de la aplicación.

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Despliégalo, lee los números y fíjate por qué la directiva prefiere mantener contratos de riesgo bajo antes que cortar de raíz y pagar altas sumas por destituciones (Compensación = $32 millones enterrados en técnicos despedidos).

> Álvaro Salinas Ortiz | alvarosalinasortiz@gmail.com | [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz)
