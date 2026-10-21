# engine/data_fetcher.py
import yfinance as yf
import pandas as pd
import requests
import time
from config import TICKERS, validate_tickers

# Session dengan User-Agent browser modern yang sangat spesifik
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
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

def fetch_market_data():
    validate_tickers(TICKERS)
    market_data = {}
    
    print("Mengambil data historis massal via yf.download (Endpoint Chart)...")
    try:
        # yf.download lebih stabil karena menggunakan endpoint 'chart' Yahoo
        # threads=False penting untuk menghindari rate limit paralel
        df_all = yf.download(TICKERS, period="1y", group_by='ticker', auto_adjust=True, threads=False, session=session)
        
        for ticker in TICKERS:
            try:
                # Ambil data spesifik per ticker dari dataframe multi-index
                hist = df_all[ticker].dropna()
                if not hist.empty and len(hist) > 50:
                    market_data[ticker] = {'history': hist}
                    print(f"  ✅ {ticker}: {len(hist)} baris harga berhasil diambil.")
                else:
                    print(f"  ⚠️ {ticker}: Data harga kosong/tidak cukup.")
                    market_data[ticker] = {'history': pd.DataFrame()}
            except KeyError:
                print(f"   {ticker}: Tidak ditemukan di dataframe download.")
                market_data[ticker] = {'history': pd.DataFrame()}
                
    except Exception as e:
        print(f"  ❌ Gagal download massal: {e}")
        for ticker in TICKERS:
            market_data[ticker] = {'history': pd.DataFrame()}

    print("\nMengambil data fundamental (info) via Ticker...")
    # Data fundamental tetap butuh Ticker.info (endpoint quoteSummary)
    # Ini adalah bagian yang paling sering diblokir Yahoo
    for ticker in TICKERS:
        info = {}
        max_retries = 2
        for attempt in range(max_retries):
            try:
                stock = yf.Ticker(ticker, session=session)
                info = stock.info
                if info and len(info) > 10: # Validasi info tidak kosong
                    break
            except Exception as e:
                print(f"  ⚠️ Retry {attempt+1} info {ticker}: {e}")
                time.sleep(5)
        
        # Fallback jika info gagal total
        if not info or len(info) <= 10:
            print(f"  ⚠️ Info {ticker} gagal, menggunakan fallback dasar.")
            info = {
                'shortName': ticker,
                'sector': 'Utilities',
                'dividendYield': 0.04,
                'payoutRatio': 0.70,
                'exDividendDate': None,
                'ticker': ticker
            }
            
        market_data[ticker]['info'] = info
        time.sleep(2) # Delay antar request info

    return market_data
