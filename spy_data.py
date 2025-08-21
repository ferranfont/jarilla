import yfinance as yf
import pandas as pd
import os
from chart_spy import create_eurusd_chart

def get_spy_data():
    spy = yf.Ticker("EURUSD=X")
    
    hist = spy.history(period="1mo")
    
    # Crear carpeta outputs y guardar CSV
    os.makedirs("outputs", exist_ok=True)
    hist.to_csv("outputs/EURUSD.csv")
    
    print("EURUSD - Últimos 6 meses:")
    print(hist.tail(10))
    print(f"💾 CSV guardado en: outputs/EURUSD.csv")
    
    info = spy.info
    print(f"\nPrecio actual: ${info.get('currentPrice', 'N/A')}")
    print(f"Precio anterior: ${info.get('previousClose', 'N/A')}")
    print(f"Volumen: {info.get('volume', 'N/A'):,}")
    
    create_eurusd_chart()

if __name__ == "__main__":
    get_spy_data()