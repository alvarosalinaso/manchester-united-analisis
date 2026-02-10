"""Módulo para carga y filtrado de datos."""
import pandas as pd
from pathlib import Path
from typing import Optional

ENTRENADORES = {
    2014: 'David Moyes',
    2015: 'Louis van Gaal', 2016: 'Louis van Gaal',
    2017: 'José Mourinho', 2018: 'José Mourinho',
    2019: 'Mourinho / Solskjær',
    2020: 'Ole Gunnar Solskjær', 2021: 'Ole Gunnar Solskjær',
    2022: 'Solskjær / Rangnick',
    2023: 'Erik ten Hag', 2024: 'Erik ten Hag'
}

def cargar_y_filtrar_datos(ruta_archivo: str = 'pl-tables-1993-2024.csv') -> Optional[pd.DataFrame]:
    """
    Carga el CSV y filtra datos relevantes para el análisis del Man Utd desde 2014.
    """
    try:
        # Intentar ruta absoluta o relativa al CWD
        path = Path(ruta_archivo).resolve()
        
        if not path.exists():
            # Intentar buscar en la raíz del proyecto si estamos corriendo desde dentro de src/tests
            # Asumimos estructura standard: project_root/pl-tables...
            # Subir hasta encontrar el archivo o fallar
            candidate = Path.cwd() / ruta_archivo
            if candidate.exists():
                path = candidate
            else:
                 # Try finding via known structure relative to this file
                 # data.py is in src/manutd_analysis/
                 # project root is ../../
                 project_root = Path(__file__).parent.parent.parent
                 candidate = project_root / ruta_archivo
                 if candidate.exists():
                     path = candidate

        if not path.exists():
            raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo} en {path}")

        df = pd.read_csv(path)
        
        # Filtro United
        united = df[(df['team'] == 'Manchester Utd') & (df['season_end_year'] >= 2014)].copy()
        
        # Selección y renombramiento de columnas
        cols_map = {
            'season_end_year': 'año',
            'points': 'pts_utd',
            'position': 'pos_utd',
            'gf': 'gf_utd',
            'ga': 'ga_utd',
            'played': 'played'
        }
        # Asegurar que existan las columnas antes de renombrar
        # (Esto asume nombres del CSV original)
        if hasattr(united, 'columns'):
             # Create DataFrame with only needed columns
             united = united[['season_end_year', 'points', 'position', 'gf', 'ga', 'played']].copy()
             united.columns = ['año', 'pts_utd', 'pos_utd', 'gf_utd', 'ga_utd', 'played']
        
        united['entrenador'] = united['año'].map(ENTRENADORES)

        # Filtro Campeones
        campeones = df[df['position'] == 1][['season_end_year', 'points', 'gf', 'ga']]
        campeones.columns = ['año', 'pts_champ', 'gf_champ', 'ga_champ']

        # Merge
        df_final = pd.merge(united, campeones, on='año')
        
        # Cálculo de KPIs básicos
        df_final['brecha_puntos'] = df_final['pts_champ'] - df_final['pts_utd']
        df_final['brecha_ataque'] = df_final['gf_champ'] - df_final['gf_utd']
        df_final['brecha_defensa'] = df_final['ga_utd'] - df_final['ga_champ']
        df_final['pts_por_gol'] = (df_final['pts_utd'] / df_final['gf_utd']).round(2)
        df_final['ppg'] = (df_final['pts_utd'] / df_final['played']).round(3)
        
        return df_final
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        return None
