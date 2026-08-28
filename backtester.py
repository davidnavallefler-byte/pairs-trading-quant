import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from data_loader import download_data
from cointegration_test import calculate_spread_and_zscore

def run_backtest(df, z_score, entry_threshold=2.0, exit_threshold=0.0):
    print(f"\n--- 4. EJECUTANDO BACKTEST (Umbral de entrada: ±{entry_threshold}) ---")
    
    # Creamos un DataFrame para organizar la estrategia
    strategy_df = pd.DataFrame(index=df.index)
    strategy_df['Z-Score'] = z_score
    strategy_df['Position'] = 0  # 1 = Long Spread, -1 = Short Spread, 0 = Sin posición
    
    # Lógica de las señales (Evitamos bucles for, usamos vectorización estilo Pandas)
    # Entramos cortos (Short Spread) cuando Z > +2
    strategy_df.loc[strategy_df['Z-Score'] > entry_threshold, 'Position'] = -1
    
    # Entramos largos (Long Spread) cuando Z < -2
    strategy_df.loc[strategy_df['Z-Score'] < -entry_threshold, 'Position'] = 1
    
    # Cerramos posiciones cuando el Z-Score vuelve a la media (cruza 0)
    # En la práctica, con pandas es más fácil decir: si no hay señal fuerte, mantenemos la anterior
    # PERO si el Z-score está cerca de 0, forzamos salida.
    strategy_df['Position'] = strategy_df['Position'].replace(0, np.nan)
    strategy_df.loc[(strategy_df['Z-Score'] > -exit_threshold) & (strategy_df['Z-Score'] < exit_threshold), 'Position'] = 0
    strategy_df['Position'] = strategy_df['Position'].ffill().fillna(0) # Mantenemos posición hasta que toque salida
    
    # ¡EVITAMOS EL LOOKAHEAD BIAS!
    # La señal generada hoy se ejecuta mañana (desplazamos 1 día)
    strategy_df['Position_T_plus_1'] = strategy_df['Position'].shift(1)
    
    # Calculamos los retornos diarios de cada activo
    strategy_df['MA_Returns'] = df['MA'].pct_change()
    strategy_df['V_Returns'] = df['V'].pct_change()
    
    # Retorno de la cartera: Si estamos Long Spread, compramos MA y vendemos V. (Y viceversa)
    # Asumimos que dividimos el capital 50/50 en cada operación
    strategy_df['Strategy_Returns'] = strategy_df['Position_T_plus_1'] * (0.5 * strategy_df['MA_Returns'] - 0.5 * strategy_df['V_Returns'])
    
    # Limpiamos NaNs
    strategy_df = strategy_df.dropna()
    
    # Calculamos el retorno acumulado
    strategy_df['Cumulative_Returns'] = (1 + strategy_df['Strategy_Returns']).cumprod()
    
    print(f"Retorno total acumulado: {(strategy_df['Cumulative_Returns'].iloc[-1] - 1) * 100:.2f}%")
    
    # Gráfico Final de Rentabilidad
    plt.figure(figsize=(12, 6))
    plt.plot(strategy_df.index, strategy_df['Cumulative_Returns'], label='Pairs Trading Strategy PnL', color='purple', linewidth=2)
    plt.axhline(1.0, color='gray', linestyle='--', alpha=0.5)
    plt.title("Rendimiento del Backtest (Pairs Trading: MA & V)", fontsize=14, fontweight='bold')
    plt.ylabel("Multiplicador de Capital (1.0 = Base)")
    plt.xlabel("Fecha")
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    
    plt.savefig('backtest_results.png', bbox_inches='tight')
    print("¡Gráfico de rentabilidad guardado como backtest_results.png!")

if __name__ == "__main__":
    df = download_data()
    # No necesitamos imprimir los gráficos anteriores, solo calcular el Z-Score
    plt.close('all') 
    z_score = calculate_spread_and_zscore(df, 'MA', 'V')
    run_backtest(df, z_score)