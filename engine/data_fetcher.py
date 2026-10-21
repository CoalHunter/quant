# engine/data_fetcher.py
import yfinance as yf
import pandas as pd
import requests
import time
from config import TICKERS, validate_tickers

# Custom session dengan User-Agent browser modern
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0'
})

def fetch_price_data():
    """Ambil data harga historis via yf.download (lebih stabil)"""
    print("\n[1/2] Mengambil data harga historis...")
    price_data = {}
    
    try:
        # yf.download menggunakan endpoint 'chart' yang lebih stabil
        df_all = yf.download(
            TICKERS, 
            period="1y", 
            group_by='ticker', 
            auto_adjust=True, 
            threads=False, 
            session=session,
            progress=False
        )
        
        for ticker in TICKERS:
            try:
                hist = df_all[ticker].dropna()
                if not hist.empty and len(hist) > 50:
                    price_data[ticker] = hist
                    print(f"  ✅ {ticker}: {len(hist)} baris harga")
                else:
                    print(f"  ️ {ticker}: Data harga tidak cukup")
                    price_data[ticker] = pd.DataFrame()
            except KeyError:
                print(f"   {ticker}: Tidak ada di dataframe")
                price_data[ticker] = pd.DataFrame()
                
    except Exception as e:
        print(f"  ❌ Gagal download massal: {e}")
        for ticker in TICKERS:
            price_data[ticker] = pd.DataFrame()
    
    return price_data

def fetch_fundamental_data():
    """Ambil data fundamental via Ticker.info dengan retry"""
    print("\n[2/2] Mengambil data fundamental...")
    fundamental_data = {}
    
    for ticker in TICKERS:
        info = {}
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                stock = yf.Ticker(ticker, session=session)
                info = stock.info
                
                # Validasi info tidak kosong
                if info and len(info) > 10:
                    print(f"  ✅ {ticker}: Data fundamental berhasil")
                    break
                else:
                    print(f"  ⚠️ {ticker}: Info kosong, retry {attempt+1}/{max_retries}")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"  ⚠️ {ticker}: Error {e}, retry {attempt+1}/{max_retries}")
                time.sleep(5)
        
        # Fallback jika info gagal total
        if not info or len(info) <= 10:
            print(f"  ⚠️ {ticker}: Menggunakan data fallback")
            info = {
                'shortName': ticker,
                'sector': 'Utilities',
                'dividendYield': 0.04,
                'payoutRatio': 0.70,
                'exDividendDate': None,
                'ticker': ticker
            }
        
        fundamental_data[ticker] = info
        time.sleep(2)  # Delay antar request
    
    return fundamental_data

def fetch_market_data():
    """Orchestrator: gabungkan harga + fundamental"""
    validate_tickers(TICKERS)
    
    price_data = fetch_price_data()
    fundamental_data = fetch_fundamental_data()
    
    market_data = {}
    for ticker in TICKERS:
        market_data[ticker] = {
            'history': price_data.get(ticker, pd.DataFrame()),
            'info': fundamental_data.get(ticker, {})
        }
    
    return market_data
