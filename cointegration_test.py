import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
import matplotlib.pyplot as plt
from data_loader import download_data

def test_cointegration(asset1, asset2):
    """Prueba estadística de Engle-Granger para cointegración."""

    score, pvalue, _ = coint(asset1, asset2)
    print(f"P-value de cointegración: {pvalue:.4f}")
    
    if pvalue < 0.05:
        print("=> ¡Estadísticamente cointegradas (p < 0.05)! Podemos operarlas.")
    else:
        print("=> Riesgo: No hay fuerte evidencia estadística de cointegración.")
    return pvalue

def calculate_spread_and_zscore(df, ticker_y, ticker_x):
    """Calcula el Hedge Ratio (Beta), el Spread y el Z-Score."""
    y = df[ticker_y]
    x = df[ticker_x]
    
    x_with_constant = sm.add_constant(x)
    model = sm.OLS(y, x_with_constant).fit()
    beta = model.params.iloc[1]  # Usamos iloc para evitar warnings
    print(f"Hedge Ratio (Beta) calculado: {beta:.4f}")
    
    spread = y - (beta * x)
    
    z_score = (spread - spread.mean()) / spread.std()
    
    plt.figure(figsize=(12, 5))
    z_score.plot(label='Z-Score (Spread)', color='teal', linewidth=1.5)
    plt.axhline(z_score.mean(), color='black', label='Media (0)', linewidth=1)
    
    plt.axhline(2.0, color='red', linestyle='--', label='Venta (Short MA, Long V)', alpha=0.7)
    plt.axhline(-2.0, color='green', linestyle='--', label='Compra (Long MA, Short V)', alpha=0.7)
    
    plt.title(f"Z-Score del Spread: {ticker_y} vs {ticker_x}", fontsize=14, fontweight='bold')
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    
    plt.savefig('z_score_spread.png', bbox_inches='tight')
    
    return z_score

if __name__ == "__main__":
    df = download_data()
    
    # Y = Mastercard (MA), X = Visa (V)
    test_cointegration(df['MA'], df['V'])
    
    z_score = calculate_spread_and_zscore(df, 'MA', 'V')