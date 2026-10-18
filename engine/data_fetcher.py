# engine/data_fetcher.py
import yfinance as yf
import pandas as pd
import time
from config import TICKERS, validate_tickers

def fetch_market_data():
    validate_tickers(TICKERS)
    market_data = {}
    
    for ticker in TICKERS:
        print(f"Fetching {ticker}...")
        stock = yf.Ticker(ticker)
        
        # Ambil data historis
        hist = stock.history(period="1y")
        
        # Ambil info dengan retry
        info = {}
        max_retries = 3
        for attempt in range(max_retries):
            try:
                info = stock.info
                if info and len(info) > 5:
                    break
            except Exception as e:
                print(f"  Retry {attempt+1}/{max_retries} for {ticker}: {e}")
                time.sleep(3)
        
        # Fallback jika info gagal
        if not info or len(info) <= 5:
            print(f"  Using fallback for {ticker}")
            info = {
                'shortName': ticker,
                'sector': 'Utilities',
                'dividendYield': 0.05,
                'payoutRatio': 0.70,
                'exDividendDate': None
            }
        
        market_data[ticker] = {
            'history': hist,
            'info': info
        }
        
        time.sleep(2)  # Delay hindari rate limit
    
    return market_data
