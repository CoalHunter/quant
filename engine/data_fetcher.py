# engine/data_fetcher.py
import yfinance as yf
import pandas as pd
import requests
import time
import json
from config import TICKERS, validate_tickers, ALPHA_VANTAGE_KEY

# Custom session untuk yfinance
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
})

def fetch_from_yfinance(ticker):
    """Sumber 1: yfinance dengan custom headers"""
    try:
        stock = yf.Ticker(ticker, session=session)
        hist = stock.history(period="1y")
        info = stock.info
        time.sleep(2)
        if not hist.empty and len(hist) > 50:
            return hist, info
    except Exception as e:
        print(f"  yfinance gagal: {e}")
    return None, None

def fetch_from_alpha_vantage(ticker):
    """Sumber 2: Alpha Vantage API"""
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={ALPHA_VANTAGE_KEY}&outputsize=full"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'Time Series (Daily)' not in data:
            print(f"  Alpha Vantage gagal: {data.get('Note', 'Unknown error')}")
            return None, None
        
        # Convert ke DataFrame
        ts = data['Time Series (Daily)']
        df = pd.DataFrame.from_dict(ts, orient='index')
        df = df.rename(columns={
            '1. open': 'Open', '2. high': 'High', 
            '3. low': 'Low', '4. close': 'Close', '5. volume': 'Volume'
        })
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df = df.tail(252)  # 1 tahun trading days
        
        # Info dasar dari Alpha Vantage
        info_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_KEY}"
        info_response = requests.get(info_url, timeout=10)
        info_data = info_response.json()
        
        info = {
            'shortName': info_data.get('Name', ticker),
            'sector': info_data.get('Sector', 'Utilities'),
            'dividendYield': float(info_data.get('DividendYield', 0)),
            'payoutRatio': float(info_data.get('PayoutRatio', 0)),
            'exDividendDate': info_data.get('ExDividendDate', None),
            'ticker': ticker
        }
        
        time.sleep(12)  # Alpha Vantage limit 5 req/menit untuk free tier
        return df, info
    except Exception as e:
        print(f"  Alpha Vantage gagal: {e}")
    return None, None

def fetch_from_stooq(ticker):
    """Sumber 3: Stooq (format ticker: WTRG.US)"""
    try:
        from pandas_datareader import data as pdr
        # Stooq butuh format ticker.US untuk saham AS
        stooq_ticker = f"{ticker}.US"
        df = pdr.DataReader(stooq_ticker, 'stooq', 
                           start=pd.Timestamp.now() - pd.DateOffset(years=1))
        df = df.sort_index()
        
        info = {
            'shortName': ticker,
            'sector': 'Utilities',
            'dividendYield': 0.05,  # Fallback
            'payoutRatio': 0.70,
            'exDividendDate': None,
            'ticker': ticker
        }
        time.sleep(1)
        return df, info
    except Exception as e:
        print(f"  Stooq gagal: {e}")
    return None, None

def fetch_market_data():
    validate_tickers(TICKERS)
    market_data = {}
    
    for ticker in TICKERS:
        print(f"\nFetching {ticker}...")
        hist, info = None, None
        
        # Coba yfinance dulu
        print("  [1/3] Mencoba yfinance...")
        hist, info = fetch_from_yfinance(ticker)
        
        # Jika gagal, coba Alpha Vantage
        if hist is None or hist.empty:
            print("  [2/3] Mencoba Alpha Vantage...")
            hist, info = fetch_from_alpha_vantage(ticker)
        
        # Jika masih gagal, coba Stooq
        if hist is None or hist.empty:
            print("  [3/3] Mencoba Stooq...")
            hist, info = fetch_from_stooq(ticker)
        
        # Jika semua gagal, pakai data dummy
        if hist is None or hist.empty:
            print(f"  ⚠️ SEMUA SUMBER GAGAL! Menggunakan data dummy untuk {ticker}")
            hist = pd.DataFrame({
                'Open': [100.0] * 100,
                'High': [102.0] * 100,
                'Low': [98.0] * 100,
                'Close': [100.0] * 100,
                'Volume': [1000000] * 100
            }, index=pd.date_range(end=pd.Timestamp.now(), periods=100, freq='D'))
            info = {
                'shortName': ticker,
                'sector': 'Utilities',
                'dividendYield': 0.05,
                'payoutRatio': 0.70,
                'exDividendDate': None,
                'ticker': ticker
            }
        
        market_data[ticker] = {'history': hist, 'info': info}
        print(f"  ✅ {ticker}: {len(hist)} rows")
    
    return market_data
