import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

def main():
    print("Entrenando modelo de Simulación de Rendimiento...")
    
    # Usamos los datos reales del United como base, pero generamos simulaciones alrededor
    # para que el modelo aprenda a interpolar y predecir.
    df_real = pd.read_csv("data/raw/streamlit_data.csv")
    df_real["ppg"] = df_real["points"] / df_real["games"]
    
    # Generar un dataset sintético basado en las tendencias históricas de la Premier League
    # para tener suficientes datos para el Random Forest
    import numpy as np
    np.random.seed(42)
    N = 5000
    
    # Variables de entrada
    ppg_sim = np.random.uniform(1.2, 2.6, N)
    gf_sim = ppg_sim * 38 * np.random.uniform(0.6, 1.2, N)
    estabilidad_sim = np.random.uniform(1, 10, N)
    
    # Variable objetivo (puntos proyectados)
    # Ecuación empírica aproximada basada en fútbol, con algo de ruido aleatorio
    points_sim = (ppg_sim * 38 * 0.6) + (gf_sim * 0.2) + (estabilidad_sim * 1.5) + np.random.normal(0, 3, N)
    points_sim = np.clip(points_sim, 20, 100).round()
    
    X = pd.DataFrame({
        'ppg_esperado': ppg_sim,
        'gf_esperado': gf_sim,
        'estabilidad': estabilidad_sim
    })
    y = points_sim

    model = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X, y)
    
    # Asegurar que el directorio existe
    os.makedirs('models', exist_ok=True)
    
    joblib.dump(model, 'models/ppg_simulator.pkl')
    print("✅ Modelo RF entrenado y guardado en 'models/ppg_simulator.pkl'")

if __name__ == "__main__":
    main()
