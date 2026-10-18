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
        
        # Ambil data historis (lebih stabil)
        hist = stock.history(period="1y")
        
        # Ambil info dengan retry mechanism
        info = {}
        max_retries = 3
        for attempt in range(max_retries):
            try:
                info = stock.info
                if info and len(info) > 5:
                    break
            except Exception as e:
                print(f"  Retry {attempt+1}/{max_retries} for {ticker} info: {e}")
                time.sleep(3)
        
        # Fallback: gunakan fast_info jika stock.info gagal total
        if not info or len(info) <= 5:
            print(f"  Using fast_info fallback for {ticker}")
            try:
                fi = stock.fast_info
                info = {
                    'shortName': ticker,
                    'sector': 'Utilities',
                    'dividendYield': getattr(fi, 'last_dividend_date', 0),
                    'payoutRatio': 0.7,
                    'exDividendDate': None
                }
            except:
                info = {'shortName': ticker, 'sector': 'Utilities'}
        
        market_data[ticker] = {
            'history': hist,
            'info': info
        }
        
        # Delay antar ticker untuk hindari rate limit
        time.sleep(2)
    
    return market_data
