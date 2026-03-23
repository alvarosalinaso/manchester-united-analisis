[![Integración Continua](https://github.com/alvarosalinaso/manchester-united-analisis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/manchester-united-analisis/actions/workflows/ci.yml)

# Manchester United: Auditoría de Gasto Neto

Análisis financiero del desgaste deportivo del Manchester United (Post-Ferguson). Esto examina cuánto dinero le costó a los dueños cada punto obtenido por cada entrenador que pasó por el banquillo en la última década.

## Flujo de Datos y Panel Visual
El repositorio expone una herramienta visual para la alta gerencia deportiva. Las métricas claves:
- **Gasto Neto por Punto**: La división pura entre la inyección de libras esterlinas al mercado de fichajes y el rendimiento real final en la tabla de posiciones.
- **Táctica contra Azar**: Mapas de correlación que verifican estadísticamente si recibir goles condena a un equipo financieramente de la misma manera que no anotarlos. 
- **Filosofía de Falla Rápida**: 
  - Código purgado de estructuras redundantes. 
  - Excepciones genéricas y ocultas removidas para evitar errores silenciosos en la ejecución visual.
  - Resolución dinámica de archivos asegurando despliegues estables sin importar desde dónde ejecutes la aplicación en tu computadora.

## Configuración Inicial
Este proyecto inicia utilizando un entorno ligero de Python. Solamente requiere instalar las dependencias visuales antes de la ejecución.

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Despliégalo, lee los números y analiza por qué la directiva prefiere mantener contratos bajos antes que pagar altas sumas por destituciones (Compensaciones históricas superan los 32 millones por técnicos despedidos).

> Álvaro Salinas Ortiz | alvarosalinasortiz@gmail.com | [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz)
