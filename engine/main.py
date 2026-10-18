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
        
        swing_data = calculate_swing(hist, info)
        div_data = calculate_dividend(info, hist)
        
        # Format Chart Data (Sampling setiap 5 hari untuk performa frontend)
        chart_dates = [d.strftime('%Y-%m-%d') for d in hist.index[::5]]
        chart_prices = [round(p, 2) for p in hist['Close'].iloc[::5].tolist()]
        chart_vols = [int(v) for v in hist['Volume'].iloc[::5].tolist()]
        
        rec = {
            "ticker": ticker,
            "name": info.get('shortName', ticker),
            "sector": info.get('sector', 'N/A'),
            "current_price": round(hist['Close'].iloc[-1], 2),
            "daily_volume": int(hist['Volume'].iloc[-1]),
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
    
    # Simpan ke output/data.json
    os.makedirs('../output', exist_ok=True)
    with open('../output/data.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
        
    print("Selesai! Data disimpan di output/data.json")

if __name__ == "__main__":
    generate_dashboard_data()
