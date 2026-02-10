"""Módulo para visualización de datos."""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False

def graficar_eficiencia_y_brecha(df: pd.DataFrame, out_dir: str = 'assets/figures'):
    """Genera gráficos comparativos de eficiencia y brecha de puntos."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Gráfico 1: Eficiencia
    resumen = df.groupby('entrenador')['pts_por_gol'].mean().sort_values(ascending=False)
    
    if HAS_SEABORN:
        sns.barplot(x=resumen.index, y=resumen.values, ax=ax1, palette='viridis')
    else:
        resumen.plot(kind='bar', ax=ax1, color='skyblue')
        
    ax1.set_title('Eficiencia Promedio (Pts/Gol)')
    ax1.set_ylabel('Puntos por Gol')
    ax1.tick_params(axis='x', rotation=45)
    
    # Gráfico 2: Brecha
    if HAS_SEABORN:
        sns.lineplot(data=df, x='año', y='brecha_puntos', marker='o', ax=ax2, color='red')
    else:
        ax2.plot(df['año'], df['brecha_puntos'], marker='o', color='red')
        
    ax2.set_title('Brecha de Puntos con el Campeón')
    ax2.set_ylabel('Brecha')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    out_path = Path(out_dir) / 'eficiencia_y_brecha.png'
    plt.savefig(out_path)
    plt.close()
    return out_path

def graficar_rentabilidad_ofensiva(df: pd.DataFrame, out_dir: str = 'assets/figures'):
    """Genera scatter plot de volumen ofensivo vs eficiencia."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    
    plt.figure(figsize=(10, 6))
    resumen = df.groupby('entrenador').agg({'gf_utd': 'mean', 'pts_por_gol': 'mean'}).reset_index()
    
    if HAS_SEABORN:
        sns.scatterplot(data=resumen, x='gf_utd', y='pts_por_gol', size=150, legend=False, hue='entrenador')
    else:
        plt.scatter(resumen['gf_utd'], resumen['pts_por_gol'], s=150)
        
    # Etiquetas
    for _, row in resumen.iterrows():
        plt.text(row['gf_utd'] + 0.5, row['pts_por_gol'], row['entrenador'], fontsize=9)
        
    # Líneas promedio
    plt.axhline(y=resumen['pts_por_gol'].mean(), color='gray', linestyle='--', alpha=0.5)
    plt.axvline(x=resumen['gf_utd'].mean(), color='gray', linestyle='--', alpha=0.5)
    
    plt.title('Rentabilidad Ofensiva: Volumen vs Eficiencia')
    plt.xlabel('Goles a Favor Promedio')
    plt.ylabel('Puntos por Gol')
    plt.grid(True, alpha=0.2)
    
    out_path = Path(out_dir) / 'rentabilidad_ofensiva.png'
    plt.savefig(out_path)
    plt.close()
    return out_path
