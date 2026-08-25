"""
Manchester United Performance Analysis (2014-2024)
Punto de entrada principal del proyecto.
"""

from causal_inference import run_causal_analysis
from cohort_analysis import run_cohort_analysis
from manutd_analysis.analysis import (
    analizar_eficiencia,
    analizar_estabilidad,
    calcular_costo_inestabilidad,
)
from manutd_analysis.data import cargar_y_filtrar_datos
from manutd_analysis.plots import (
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

    # Inferencia causal
    print("\n--- 🔬 INFERENCIA CAUSAL (DiD) ---")
    causal = run_causal_analysis()
    if causal and "did_summary" in causal:
        summary = causal["did_summary"]
        print(f"  Cambios analizados: {summary['n_changes']}")
        print(f"  Cambios significativos: {summary['n_significant']}")
        print(f"  ATT promedio: {summary['mean_att']:+.1f} pts")

    # Análisis de cohortes
    print("\n--- 📊 ANÁLISIS DE COHORTES ---")
    cohort = run_cohort_analysis()
    if cohort and "retention_summary" in cohort:
        rs = cohort["retention_summary"]
        print(f"  Gestores analizados: {rs['n_managers']}")
        print(f"  Tenencia promedio: {rs['avg_tenure']} temporadas")
        print(f"  Tasa de rotación: {rs['turnover_rate']} gestores/década")

    # Statistical tests
    from src.statistical_tests import run_statistical_tests
    run_statistical_tests()

    # Generate executive tables
    from src.generate_tables import generate as generate_exec_tables
    generate_exec_tables()

    # Generate paper report
    from src.generate_report import generate_report
    generate_report()

    # Conclusiones
    imprimir_conclusiones(df)
    print("\n✅ Análisis completado.")


if __name__ == "__main__":
    main()
