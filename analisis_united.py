"""
analisis_united.py — Script legado (mantenido por compatibilidad).

Para el análisis completo usa `main.py` o importa desde `src/manutd_analysis/`.
"""
# Este archivo existía con código duplicado. Ahora delega al paquete principal.
from src.manutd_analysis.data import cargar_y_filtrar_datos, ENTRENADORES
from src.manutd_analysis.analysis import (
    analizar_eficiencia,
    analizar_estabilidad,
    calcular_costo_inestabilidad,
)
from src.manutd_analysis.plots import (
    graficar_eficiencia_y_brecha,
    graficar_rentabilidad_ofensiva,
)

__all__ = [
    "cargar_y_filtrar_datos",
    "ENTRENADORES",
    "analizar_eficiencia",
    "analizar_estabilidad",
    "calcular_costo_inestabilidad",
    "graficar_eficiencia_y_brecha",
    "graficar_rentabilidad_ofensiva",
]
