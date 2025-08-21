import yfinance as yf
import pandas as pd
from chart_spy import create_eurusd_chart

def get_spy_data():
    spy = yf.Ticker("EURUSD=X")
    
    hist = spy.history(period="1mo")
    
    print("EURUSD - Últimos 6 meses:")
    print(hist.tail(10))
    
    info = spy.info
    print(f"\nPrecio actual: ${info.get('currentPrice', 'N/A')}")
    print(f"Precio anterior: ${info.get('previousClose', 'N/A')}")
    print(f"Volumen: {info.get('volume', 'N/A'):,}")
    
    create_eurusd_chart()

if __name__ == "__main__":
    get_spy_data()