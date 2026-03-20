"""
Manchester United Performance Analysis (2014-2024)
Punto de entrada principal del proyecto.
"""
from src.manutd_analysis.data import cargar_y_filtrar_datos
from src.manutd_analysis.analysis import (
    analizar_eficiencia,
    analizar_estabilidad,
    calcular_costo_inestabilidad,
)
from src.manutd_analysis.plots import (
    graficar_eficiencia_y_brecha,
    graficar_rentabilidad_ofensiva,
)


def imprimir_conclusiones(df):
    """Imprime las conclusiones finales del análisis."""
    print("\n" + "=" * 60)
    print("📜 CONCLUSIONES: LA DÉCADA DE LA IRREGULARIDAD")
    print("=" * 60)
    print(f"  · Brecha promedio con el campeón : {df['brecha_puntos'].mean():.1f} pts")
    print(f"  · Brecha ofensiva media          : {df['brecha_ataque'].mean():.1f} goles")
    print(f"  · PPG promedio del período        : {df['ppg'].mean():.3f}")

    comparativa = analizar_estabilidad(df)
    costo = calcular_costo_inestabilidad(comparativa)
    print(f"  · Costo de la inestabilidad       : ~{costo:.1f} pts por temporada de transición")
    print("=" * 60)


def main():
    print("🔄 Cargando datos...")
    df = cargar_y_filtrar_datos()

    if df is None:
        print("❌ No se pudieron cargar los datos. Verifica que 'pl-tables-1993-2024.csv' exista.")
        return

    print(f"✅ Datos cargados: {len(df)} temporadas analizadas.\n")

    # Análisis
    print("--- 📈 EFICIENCIA POR ENTRENADOR (Pts/Gol) ---")
    print(analizar_eficiencia(df).to_string())

    print("\n--- ⚠️  IMPACTO DE LA INESTABILIDAD ---")
    comparativa = analizar_estabilidad(df)
    print(comparativa.to_string())

    # Visualizaciones
    print("\n🎨 Generando gráficos...")
    graficar_eficiencia_y_brecha(df)
    graficar_rentabilidad_ofensiva(df)

    # Conclusiones
    imprimir_conclusiones(df)
    print("\n✅ Análisis completado.")


if __name__ == "__main__":
    main()
