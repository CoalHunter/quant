# engine/main.py
import json
import os
from datetime import datetime
from data_fetcher import fetch_market_data
from quant_logic import calculate_swing, calculate_dividend

def generate_dashboard_data():
    print("Memulai proses kuantitatif...")
    market_data = fetch_market_data()
    recommendations = []
    
    for ticker, data in market_data.items():
        hist = data['history']
        info = data['info']
        
        print(f"Memproses {ticker}...")
        
        swing_data = calculate_swing(hist, info)
        div_data = calculate_dividend(info, hist)
        
        # Handle chart data dengan aman
        if not hist.empty and 'Close' in hist.columns:
            # Pastikan index adalah datetime
            if not isinstance(hist.index, pd.DatetimeIndex):
                hist.index = pd.to_datetime(hist.index)
                
            chart_dates = [d.strftime('%Y-%m-%d') for d in hist.index[::5]]
            chart_prices = [round(float(p), 2) for p in hist['Close'].iloc[::5].tolist()]
            chart_vols = [int(v) for v in hist['Volume'].iloc[::5].tolist()]
            current_price = round(float(hist['Close'].iloc[-1]), 2)
            daily_volume = int(hist['Volume'].iloc[-1])
        else:
            chart_dates = []
            chart_prices = []
            chart_vols = []
            current_price = 0
            daily_volume = 0
        
        rec = {
            "ticker": ticker,
            "name": info.get('shortName', ticker),
            "sector": info.get('sector', 'N/A'),
            "current_price": current_price,
            "daily_volume": daily_volume,
            "swing_strategy": swing_data,
            "dividend_strategy": div_data,
            "chart_data": {
                "dates": chart_dates,
                "prices": chart_prices,
                "volumes": chart_vols
            }
        }
        recommendations.append(rec)
        
    output = {
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "market": "US Domestic Infrastructure"
        },
        "recommendations": recommendations
    }
    
    os.makedirs('../output', exist_ok=True)
    with open('../output/data.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
        
    print("Selesai! Data disimpan di output/data.json")

if __name__ == "__main__":
    import pandas as pd # Tambahkan import ini di main.py
    generate_dashboard_data()
