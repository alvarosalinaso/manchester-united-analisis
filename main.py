from src.manutd_analysis.data import load_raw_data
from src.manutd_analysis.analysis import get_efficiency_df, get_stability_df, calc_instability_cost
from src.manutd_analysis.plots import graficar_eficiencia_y_brecha, graficar_rentabilidad_ofensiva

def dump_stats(df):
    print("\n--- RESUMEN DÉCADA POST-FERGUSON ---")
    print(f"Brecha media vs 1ero: {df['brecha_puntos'].mean():.1f} pts")
    print(f"Brecha goles media: {df['brecha_ataque'].mean():.1f}")
    print(f"PPG Acumulado: {df['ppg'].mean():.3f}")

    stab_df = get_stability_df(df)
    cost = calc_instability_cost(stab_df)
    print(f"Costo por despidos y transición: ~{cost:.1f} pts perdidos al año")
    print("------------------------------------\n")

def run():
    print("Loading datasets...")
    df = load_raw_data()
    if df is None:
        print("Falla total: no se encontró pl-tables-1993-2024.csv")
        return

    print(f"OK. {len(df)} temporadas parseadas.\n")

    print("> EFICIENCIA DE DTs (Pts/Gol)")
    print(get_efficiency_df(df).to_string())

    print("\n> IMPACTO DE LA MÁQUINA DE DESPIDOS")
    stab_df = get_stability_df(df)
    print(stab_df.to_string())

    print("\nGenerando charts...")
    graficar_eficiencia_y_brecha(df)
    graficar_rentabilidad_ofensiva(df)

    dump_stats(df)
    print("Listo.")

if __name__ == "__main__":
    run()
