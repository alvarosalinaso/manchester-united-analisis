# Manchester United Performance Analysis (2014-2024)

Análisis detallado del rendimiento del Manchester United en la Premier League post-Ferguson. Identifica patrones de irregularidad y cuantifica el costo de la inestabilidad.

## 📊 Objetivo
Demostrar con datos cómo la falta de consistencia en el banquillo ha costado puntos y títulos, proporcionando métricas claras de eficiencia por entrenador.

## 🛠️ Tecnologías
- **Python 3.8+**
- **Pandas**: Procesamiento de datos.
- **Seaborn / Matplotlib**: Visualización de datos de alta calidad.
- **Pytest**: Pruebas automatizadas.

## 📁 Estructura
```
manchester-united-analisis/
├── src/
│   └── manutd_analysis/  # Paquete principal
│       ├── data.py       # Carga de datos
│       ├── analysis.py   # Lógica de métricas
│       └── plots.py      # Gráficos
├── tests/                # Tests unitarios
├── assets/               # Gráficos generados y datos
└── pyproject.toml        # Configuración del proyecto
```

## 🚀 Inicio Rápido

1.  **Instalar dependencias**:
    ```bash
    pip install -e .
    ```

2.  **Correr los tests**:
    ```bash
    pytest
    ```

3.  **Generar análisis**:
    Puedes importar el paquete en tus scripts:
    ```python
    from manutd_analysis.data import cargar_y_filtrar_datos
    from manutd_analysis.plots import graficar_rentabilidad_ofensiva
    
    df = cargar_y_filtrar_datos()
    graficar_rentabilidad_ofensiva(df)
    ```

## 📈 Resultados Clave
- **Brecha con el Campeón**: ~20 puntos promedio por temporada.
- **Costo de Inestabilidad**: Los años con cambio de DT cuestan puntos significativos.
- **Eficiencia**: Mourinho y Van Gaal mostraron la mejor relación puntos/gol.

## 📞 Contacto
- **Autor**: Álvaro Salinas Ortiz
- **Email**: alvarosalinasortiz@gmail.com
