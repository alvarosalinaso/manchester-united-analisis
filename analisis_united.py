# Manchester United Performance Analysis (2014-2024)
# Análisis de rendimiento del Manchester United en la Premier League desde 2014
# Proyecto de portafolio para demostrar habilidades en análisis de datos deportivos

import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# CONFIGURACIÓN Y CONSTANTES
# ==========================================
ENTRENADORES = {
    2014: 'David Moyes',
    2015: 'Louis van Gaal', 2016: 'Louis van Gaal',
    2017: 'José Mourinho', 2018: 'José Mourinho',
    2019: 'Mourinho / Solskjær',
    2020: 'Ole Gunnar Solskjær', 2021: 'Ole Gunnar Solskjær',
    2022: 'Solskjær / Rangnick',
    2023: 'Erik ten Hag', 2024: 'Erik ten Hag'
}

BIG_SIX = ['Manchester Utd', 'Manchester City', 'Liverpool', 'Arsenal', 'Chelsea', 'Tottenham']

# ==========================================
# FUNCIONES DE PREPARACIÓN DE DATOS
# ==========================================
def cargar_y_filtrar_datos(ruta_archivo):
    """
    Carga el CSV y filtra datos relevantes para el análisis.
    
    Args:
        ruta_archivo (str): Ruta al archivo CSV con datos de la Premier League.
    
    Returns:
        pd.DataFrame: DataFrame maestro con datos de United y campeones.
    """
    try:
        df = pd.read_csv(ruta_archivo)
        
        # Filtro United
        united = df[(df['team'] == 'Manchester Utd') & (df['season_end_year'] >= 2014)].copy()
        united = united[['season_end_year', 'points', 'position', 'gf', 'ga']]
        united.columns = ['año', 'pts_utd', 'pos_utd', 'gf_utd', 'ga_utd']
        united['entrenador'] = united['año'].map(ENTRENADORES)

        # Filtro Campeones
        campeones = df[df['position'] == 1][['season_end_year', 'points', 'gf', 'ga']]
        campeones.columns = ['año', 'pts_champ', 'gf_champ', 'ga_champ']

        # Merge y KPIs
        df_final = pd.merge(united, campeones, on='año')
        df_final['brecha_puntos'] = df_final['pts_champ'] - df_final['pts_utd']
        df_final['brecha_ataque'] = df_final['gf_champ'] - df_final['gf_utd']
        df_final['brecha_defensa'] = df_final['ga_utd'] - df_final['ga_champ']
        df_final['pts_por_gol'] = (df_final['pts_utd'] / df_final['gf_utd']).round(2)
        
        return df_final
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        return None

# ==========================================
# FUNCIONES DE ANÁLISIS
# ==========================================
def analizar_eficiencia(df):
    """
    Analiza la eficiencia de puntos por gol por entrenador.
    
    Args:
        df (pd.DataFrame): DataFrame maestro.
    """
    print("\n--- 📈 ANÁLISIS DE EFICIENCIA POR ENTRENADOR ---")
    resumen = df.groupby('entrenador')['pts_por_gol'].mean().sort_values(ascending=False)
    print(resumen)

def analizar_estabilidad(df):
    """
    Analiza el impacto de la inestabilidad (cambios de entrenador).
    
    Args:
        df (pd.DataFrame): DataFrame maestro.
    """
    df['es_transicion'] = df['entrenador'].str.contains('/')
    comparativa = df.groupby('es_transicion')[['pts_utd', 'brecha_puntos', 'gf_utd']].mean().round(1)
    comparativa.index = ['Estable (1 Técnico)', 'Transición (Relevo)']
    
    print("\n--- ⚠️ IMPACTO DE LA INESTABILIDAD EN EL RENDIMIENTO ---")
    print(comparativa)
    
    pts_perdidos = comparativa.loc['Estable (1 Técnico)', 'pts_utd'] - comparativa.loc['Transición (Relevo)', 'pts_utd']
    print(f"\n💡 CONCLUSIÓN: Los años de cambio de técnico cuestan ~{pts_perdidos:.1f} puntos por temporada.")

# ==========================================
# FUNCIONES DE VISUALIZACIÓN
# ==========================================
def graficar_eficiencia_y_brecha(df):
    """
    Genera gráficos de eficiencia y brecha de puntos.
    
    Args:
        df (pd.DataFrame): DataFrame maestro.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Gráfico de barras: Eficiencia
    resumen = df.groupby('entrenador')['pts_por_gol'].mean().sort_values(ascending=False)
    resumen.plot(kind='bar', ax=ax1, color='skyblue')
    ax1.set_title('Eficiencia Promedio (Puntos por Gol) por Entrenador')
    ax1.set_ylabel('Puntos por Gol')
    ax1.tick_params(axis='x', rotation=45)
    
    # Gráfico de líneas: Brecha
    ax2.plot(df['año'], df['brecha_puntos'], marker='o', color='red')
    ax2.set_title('Brecha de Puntos con el Campeón por Año')
    ax2.set_xlabel('Año')
    ax2.set_ylabel('Brecha de Puntos')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('eficiencia_y_brecha.png')
    plt.close()
    print("✅ Gráfico guardado como 'eficiencia_y_brecha.png'")

def graficar_rentabilidad_ofensiva(df):
    """
    Genera gráfico de scatter para rentabilidad ofensiva.
    
    Args:
        df (pd.DataFrame): DataFrame maestro.
    """
    plt.figure(figsize=(10, 6))
    resumen = df.groupby('entrenador').agg({'gf_utd': 'mean', 'pts_por_gol': 'mean'}).reset_index()
    
    for _, row in resumen.iterrows():
        plt.scatter(row['gf_utd'], row['pts_por_gol'], s=150)
        plt.text(row['gf_utd'] + 0.5, row['pts_por_gol'], row['entrenador'], fontsize=9)
    
    plt.axhline(y=resumen['pts_por_gol'].mean(), color='gray', linestyle='--', alpha=0.5)
    plt.axvline(x=resumen['gf_utd'].mean(), color='gray', linestyle='--', alpha=0.5)
    plt.title('Rentabilidad Ofensiva: Volumen vs Eficiencia')
    plt.xlabel('Goles a Favor Promedio')
    plt.ylabel('Puntos por Gol')
    plt.grid(True, alpha=0.2)
    plt.savefig('rentabilidad_ofensiva.png')
    plt.close()
    print("✅ Gráfico guardado como 'rentabilidad_ofensiva.png'")

# ==========================================
# EXPORTACIÓN Y CONCLUSIONES
# ==========================================
def exportar_csv(df, nombre_archivo='analisis_united_2014_2024.csv'):
    """
    Exporta el DataFrame a CSV para uso en herramientas de visualización externas.
    
    Args:
        df (pd.DataFrame): DataFrame a exportar.
        nombre_archivo (str): Nombre del archivo CSV.
    """
    df.to_csv(nombre_archivo, index=False)
    print(f"✅ Datos exportados a '{nombre_archivo}'")

def imprimir_conclusiones(df):
    """
    Imprime las conclusiones finales del análisis.
    
    Args:
        df (pd.DataFrame): DataFrame maestro.
    """
    print("\n" + "="*60)
    print("📜 CONCLUSIONES: LA DÉCADA DE LA IRREGULARIDAD")
    print("="*60)
    print(f"1. Brecha promedio con el campeón: {df['brecha_puntos'].mean():.1f} puntos.")
    print(f"2. Brecha ofensiva: {df['brecha_ataque'].mean():.1f} goles.")
    print("3. La inestabilidad en el banquillo reduce el rendimiento significativamente.")
    print("="*60)

# ==========================================
# EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    archivo = 'pl-tables-1993-2024.csv'
    df_maestro = cargar_y_filtrar_datos(archivo)
    
    if df_maestro is not None:
        # Análisis
        analizar_eficiencia(df_maestro)
        analizar_estabilidad(df_maestro)
        
        # Visualizaciones
        graficar_eficiencia_y_brecha(df_maestro)
        graficar_rentabilidad_ofensiva(df_maestro)
        
        # Exportación
        exportar_csv(df_maestro)
        
        # Conclusiones
        imprimir_conclusiones(df_maestro)
    else:
        print("Error: No se pudieron cargar los datos.")