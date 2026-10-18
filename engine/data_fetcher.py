# engine/data_fetcher.py
import yfinance as yf
import pandas as pd
from config import TICKERS, validate_tickers

def fetch_market_data():
    validate_tickers(TICKERS)
    
    market_data = {}
    
    for ticker in TICKERS:
        print(f"Fetching data for {ticker}...")
        stock = yf.Ticker(ticker)
        
        # Ambil data historis 1 tahun untuk kalkulasi teknikal
        hist = stock.history(period="1y")
        
        # Ambil info dasar & fundamental
        info = stock.info
        
        market_data[ticker] = {
            'history': hist,
            'info': info
        }
        
    return market_data

if __name__ == "__main__":
    data = fetch_market_data()
    print(f"Berhasil mengambil data untuk {len(data)} ticker.")
    for t, d in data.items():
        print(f"{t}: {len(d['history'])} baris data historis.")
