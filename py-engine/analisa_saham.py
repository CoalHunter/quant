#!/usr/bin/env python3
import yfinance as yf
import json
import os
from datetime import datetime

# Stock list
SAHAM = {
    "SO": "Southern Company",
    "ED": "Consolidated Edison",
    "O": "Realty Income Corporation",
    "WTRG": "Waterstone Financial Inc"
}

def get_stock_data(symbol, name):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    
    current_price = round(info.get('regularMarketPrice', 0), 2)
    week52_low = round(info.get('fiftyTwoWeekLow', 0), 2)
    week52_high = round(info.get('fiftyTwoWeekHigh', 0), 2)
    
    # Historical data for indicators
    hist = ticker.history(period='3mo')
    if len(hist) < 50:
        ma20 = current_price
        ma50 = current_price
        rsi = 50.0
    else:
        ma20 = round(hist['Close'].tail(20).mean(), 2)
        ma50 = round(hist['Close'].tail(50).mean(), 2)
        
        # Simple RSI calculation
        delta = hist['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        rsi = round(100 - (100 / (1 + rs.iloc[-1])), 1)
    
    # Dividend data
    div_yield = info.get('dividendYield', 0) * 100
    div_rate = info.get('dividendRate', 0)
    
    # === SWING ANALYSIS ===
    zone_low = round(ma20 * 0.98, 2)
    zone_high = round(ma20 * 1.01, 2)
    entry_zone = f"{zone_low} - {zone_high}"
    
    target_price = round(week52_high * 0.95, 2)
    potential_gain = round(((target_price - current_price) / current_price) * 100, 1)
    
    if rsi < 35 and current_price <= zone_high:
        swing_condition = "STRONG BUY ZONE"
        swing_advice = "Excellent entry zone — accumulate now"
    elif rsi < 50 and current_price <= zone_high:
        swing_condition = "BUY ZONE"
        swing_advice = "Buy gradually at this price level"
    else:
        swing_condition = "WAIT"
        swing_advice = "Wait for price to drop into the entry zone"
    
    swing_reasons = []
    if rsi < 40:
        swing_reasons.append(f"RSI is low ({rsi}) — price may be oversold")
    elif rsi > 70:
        swing_reasons.append(f"RSI is high ({rsi}) — avoid chasing price")
    else:
        swing_reasons.append(f"RSI is neutral at {rsi}")
    
    if current_price < ma20:
        swing_reasons.append(f"Price below MA20 — near support at ${ma20}")
    elif current_price > ma20:
        swing_reasons.append(f"Price above MA20 — short-term uptrend")
    
    # === DIVIDEND ANALYSIS ===
    max_yield = round(div_yield * 1.1, 1) if div_yield > 0 else 0
    buy_zone_min = round(week52_high / (1 + (max_yield / 100)), 2) if max_yield > 0 else week52_low
    buy_zone_max = round(week52_low * 1.03, 2)
    best_buy_zone = f"{buy_zone_min} - {buy_zone_max}"
    
    price_upside = round(((week52_high - current_price) / current_price) * 100, 1)
    
    if div_yield >= 4.5 and current_price <= buy_zone_max:
        div_rating = "BEST BUY"
        div_advice = "Excellent yield — strong long-term holding candidate"
    elif div_yield >= 3.5:
        div_rating = "ATTRACTIVE"
        div_advice = "Good yield — consider gradual accumulation"
    elif div_yield < 3.0:
        div_rating = "EXPENSIVE"
        div_advice = "Price is too high for this yield — wait for pullback"
    else:
        div_rating = "FAIR"
        div_advice = "Reasonable, but better entry may appear later"
    
    div_reasons = []
    div_reasons.append(f"Current yield: {round(div_yield, 2)}%")
    div_reasons.append("Consistent dividend payer historically")
    if price_upside > 10:
        div_reasons.append(f"Potential price appreciation: {price_upside}%")
    
    return {
        "symbol": symbol,
        "name": name,
        "current_price": f"{current_price:.2f}",
        "price_52week": {
            "low": f"{week52_low:.2f}",
            "high": f"{week52_high:.2f}"
        },
        "indicators": {
            "rsi": f"{rsi:.1f}",
            "ma20": f"{ma20:.2f}",
            "ma50": f"{ma50:.2f}"
        },
        "swing": {
            "condition": swing_condition,
            "entry_zone": entry_zone,
            "target_price": f"{target_price:.2f}",
            "potential_gain_percent": f"{potential_gain:.1f}",
            "reasons": swing_reasons,
            "advice": swing_advice
        },
        "dividend": {
            "rating": div_rating,
            "current_yield_percent": f"{div_yield:.2f}",
            "max_yield_percent": f"{max_yield:.2f}",
            "best_buy_zone": best_buy_zone,
            "price_upside_percent": f"{price_upside:.1f}",
            "reasons": div_reasons,
            "advice": div_advice
        }
    }

def main():
    print("🔄 Starting stock analysis...")
    results = []
    
    for symbol, name in SAHAM.items():
        print(f"  → Processing {symbol}: {name}")
        try:
            data = get_stock_data(symbol, name)
            results.append(data)
        except Exception as e:
            print(f"  ⚠️ Failed to fetch {symbol}: {e}")
    
    output = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_stocks": len(results),
        "stock_list": results
    }
    
    os.makedirs("output", exist_ok=True)
    with open("output/hasil_analisa.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Done! Data saved to: output/hasil_analisa.json")
    print(f"📊 Total stocks processed: {len(results)}")

if __name__ == "__main__":
    main()
