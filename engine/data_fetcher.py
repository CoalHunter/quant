# engine/data_fetcher.py
import pandas as pd
from pandas_datareader import data as pdr
from yahooquery import Ticker
import time
from config import TICKERS, validate_tickers

def fetch_market_data():
    validate_tickers(TICKERS)
    market_data = {}
    
    print("Mengambil data historis dari Stooq (Anti Rate Limit)...")
    for ticker in TICKERS:
        try:
            # Stooq sangat stabil untuk data OHLCV
            df = pdr.DataReader(ticker, 'stooq', start=pd.Timestamp.now() - pd.DateOffset(years=1))
            # Stooq mengembalikan index terbalik, kita urutkan
            df = df.sort_index()
            market_data[ticker] = {'history': df}
        except Exception as e:
            print(f"  Error Stooq {ticker}: {e}. Menggunakan fallback...")
            market_data[ticker] = {'history': pd.DataFrame()}
        time.sleep(1)

    print("Mengambil data fundamental dari Yahooquery...")
    # Yahooquery bisa mengambil banyak ticker sekaligus, lebih efisien
    try:
        yq_tickers = Ticker(' '.join(TICKERS))
        summary_detail = yq_tickers.summary_detail
        profile = yq_tickers.asset_profile
        
        for ticker in TICKERS:
            info = {}
            if ticker in summary_detail:
                info = summary_detail[ticker]
            if ticker in profile:
                info.update(profile[ticker])
            
            # Normalisasi data agar cocok dengan logic lama
            market_data[ticker]['info'] = {
                'shortName': info.get('shortName', ticker),
                'sector': info.get('sector', 'Utilities'),
                'dividendYield': info.get('dividendYield', 0),
                'payoutRatio': info.get('payoutRatio', 0),
                'exDividendDate': info.get('exDividendDate', None),
                'ticker': ticker
            }
    except Exception as e:
        print(f"  Error Yahooquery: {e}. Menggunakan fallback fundamental.")
        for ticker in TICKERS:
            market_data[ticker]['info'] = {
                'shortName': ticker, 'sector': 'Utilities', 
                'dividendYield': 0.05, 'payoutRatio': 0.70, 
                'exDividendDate': None, 'ticker': ticker
            }

    return market_data
