import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from data_loader import download_data
from cointegration_test import calculate_spread_and_zscore

def run_backtest(df, z_score, entry_threshold=2.0, exit_threshold=0.0):
    print(f"\n--- 4. EJECUTANDO BACKTEST (Umbral de entrada: ±{entry_threshold}) ---")
    
    strategy_df = pd.DataFrame(index=df.index)
    strategy_df['Z-Score'] = z_score
    strategy_df['Position'] = 0  
    

    strategy_df.loc[strategy_df['Z-Score'] > entry_threshold, 'Position'] = -1
    
    strategy_df.loc[strategy_df['Z-Score'] < -entry_threshold, 'Position'] = 1
    
    strategy_df['Position'] = strategy_df['Position'].replace(0, np.nan)
    strategy_df.loc[(strategy_df['Z-Score'] > -exit_threshold) & (strategy_df['Z-Score'] < exit_threshold), 'Position'] = 0
    strategy_df['Position'] = strategy_df['Position'].ffill().fillna(0) # Mantenemos posición hasta que toque salida
    
    strategy_df['Position_T_plus_1'] = strategy_df['Position'].shift(1)
    
    strategy_df['MA_Returns'] = df['MA'].pct_change()
    strategy_df['V_Returns'] = df['V'].pct_change()
    
    strategy_df['Strategy_Returns'] = strategy_df['Position_T_plus_1'] * (0.5 * strategy_df['MA_Returns'] - 0.5 * strategy_df['V_Returns'])

    strategy_df = strategy_df.dropna()

    strategy_df['Cumulative_Returns'] = (1 + strategy_df['Strategy_Returns']).cumprod()
    
    print(f"Retorno total acumulado: {(strategy_df['Cumulative_Returns'].iloc[-1] - 1) * 100:.2f}%")

    plt.figure(figsize=(12, 6))
    plt.plot(strategy_df.index, strategy_df['Cumulative_Returns'], label='Pairs Trading Strategy PnL', color='purple', linewidth=2)
    plt.axhline(1.0, color='gray', linestyle='--', alpha=0.5)
    plt.title("Backtest Performance (Pairs Trading: MA & V)", fontsize=14, fontweight='bold')
    plt.ylabel("Capital Multiplier (1.0 = Base)")
    plt.xlabel("Date")
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    
    plt.savefig('backtest_results.png', bbox_inches='tight')
    print("¡Gráfico de rentabilidad guardado como backtest_results.png!")

if __name__ == "__main__":
    df = download_data()
    plt.close('all') 
    z_score = calculate_spread_and_zscore(df, 'MA', 'V')
    run_backtest(df, z_score)