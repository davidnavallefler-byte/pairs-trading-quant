import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def download_data():
    tickers = ['V', 'MA']
    data = yf.download(tickers, start='2020-01-01', end='2024-01-01')['Close']
    data = data.dropna()
    
    normalized_data = (data / data.iloc[0]) * 100
    
    plt.figure(figsize=(10, 5))
    plt.plot(normalized_data['V'], label='Visa (V)', color='navy')
    plt.plot(normalized_data['MA'], label='Mastercard (MA)', color='darkorange')
    plt.title("Normalized Prices: Visa vs Mastercard (2020-2024)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.savefig('pairs_visual.png', bbox_inches='tight')
    return data

if __name__ == "__main__":
    df = download_data()