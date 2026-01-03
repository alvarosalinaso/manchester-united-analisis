import pandas as pd
import matplotlib.pyplot as plt

def cargar_datos(ruta_archivo):
    """
    Carga el dataset de la Premier League y maneja errores comunes.
    """
    try:
        df = pd.read_csv(ruta_archivo)
        print(f"✅ Dataset cargado correctamente: {df.shape[0]} registros encontrados.")
        return df
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo CSV. Verifica la ruta.")
        return None

def preparar_datos(df):
    """
    Limpieza y creación de métricas avanzadas para el análisis de fútbol.
    """
    # Como analistas, sabemos que la liga cambió de 42 a 38 partidos en la temporada 95/96.
    # Para comparar el rendimiento históricamente, creamos la métrica 'Points Per Game' (PPG).
    df['ppg'] = df['points'] / df['played']
    
    # Redondeamos a 2 decimales para facilitar la lectura
    df['ppg'] = df['ppg'].round(2)
    return df

def analizar_campeones(df):
    """
    Filtra y analiza el rendimiento histórico de los ganadores de la liga.
    """
    # Filtramos solo la posición 1 (Campeones)
    campeones = df[df['position'] == 1].copy()
    
    # Ordenamos cronológicamente
    campeones = campeones.sort_values('season_end_year')
    
    # Seleccionamos columnas clave para el reporte
    cols_interes = ['season_end_year', 'team', 'played', 'points', 'ppg', 'won', 'lost']
    return campeones[cols_interes]

def visualizar_evolucion(campeones):
    """
    Genera un gráfico de línea mostrando la dificultad para ganar la liga a lo largo del tiempo.
    """
    plt.figure(figsize=(12, 6))
    
    # Graficamos los Puntos por Partido (PPG) para ser justos entre eras
    plt.plot(campeones['season_end_year'], campeones['ppg'], marker='o', linestyle='-', color='#38003c', label='Puntos por Partido')
    
    plt.title('Evolución del Rendimiento del Campeón (1993-2024)', fontsize=14, fontweight='bold')
    plt.xlabel('Temporada', fontsize=12)
    plt.ylabel('Puntos por Partido (PPG)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.axhline(y=campeones['ppg'].mean(), color='r', linestyle=':', label=f'Promedio Histórico ({campeones["ppg"].mean():.2f})')
    plt.legend()
    
    print("\n📊 Generando gráfico de evolución...")
    plt.show()

def main():
    archivo = 'pl-tables-1993-2024.csv'
    
    # 1. Ingesta de datos
    df = cargar_datos(archivo)
    
    if df is not None:
        # 2. Procesamiento
        df = preparar_datos(df)
        
        # 3. Análisis
        print("\n--- 🏆 Análisis de Campeones Históricos ---")
        df_campeones = analizar_campeones(df)
        print(df_campeones.head())
        
        # 4. Visualización
        visualizar_evolucion(df_campeones)

if __name__ == "__main__":
    main()