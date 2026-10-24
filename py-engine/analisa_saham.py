#!/usr/bin/env python3
import yfinance as yf
import json
import os
from datetime import datetime

# Stock list
STOCKS = {
    "SO": "Southern Company",
    "ED": "Consolidated Edison",
    "O": "Realty Income Corporation",
    "WTRG": "Waterstone Financial Inc"
}

def analyze_stock(symbol, name):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    
    # Price data
    current_price = round(info.get('regularMarketPrice', 0), 2)
    week52_low = round(info.get('fiftyTwoWeekLow', 0), 2)
    week52_high = round(info.get('fiftyTwoWeekHigh', 0), 2)
    
    # Historical data for indicators
    hist = ticker.history(period='3mo')
    if len(hist) >= 50:
        ma20 = round(hist['Close'].tail(20).mean(), 2)
        ma50 = round(hist['Close'].tail(50).mean(), 2)
        
        # Calculate RSI(14)
        delta = hist['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = round((100 - (100 / (1 + rs.iloc[-1]))), 1)
    else:
        ma20 = current_price
        ma50 = current_price
        rsi = 50.0
    
    # Dividend data
    dividend_yield = round(info.get('dividendYield', 0) * 100, 2)
    
    # === SWING TRADING ANALYSIS ===
    zone_low = round(ma20 * 0.98, 2)
    zone_high = round(ma20 * 1.01, 2)
    entry_zone = f"{zone_low} - {zone_high}"
    target_price = round(week52_high * 0.95, 2)
    potential_gain = round(((target_price - current_price) / current_price) * 100, 1)
    
    if rsi < 35 and current_price <= zone_high:
        swing_condition = "STRONG BUY"
        swing_advice = "Excellent entry zone — price is oversold and within entry range."
    elif rsi < 50 and current_price <= zone_high:
        swing_condition = "BUY ZONE"
        swing_advice = "Price is within reasonable entry range. Consider buying gradually."
    else:
        swing_condition = "WAIT"
        swing_advice = "Wait for better price or lower RSI before entering."
    
    swing_reasons = [
        f"RSI at {rsi} indicates {'oversold' if rsi < 35 else 'neutral' if rsi < 50 else 'overbought'} conditions.",
        f"Price {'above' if current_price > ma20 else 'below'} MA20 trend."
    ]
    
    # === DIVIDEND STRATEGY ANALYSIS ===
    max_yield_possible = round(dividend_yield * 1.1, 2) if dividend_yield > 0 else 0
    buy_zone_max = round(week52_low * 1.03, 2)
    best_buy_zone = f"{week52_low} - {buy_zone_max}"
    price_upside = round(((week52_high - current_price) / current_price) * 100, 1)
    
    if dividend_yield >= 4.5 and current_price <= buy_zone_max:
        div_rating = "BEST BUY"
        div_advice = "Excellent yield at a price near 52-week low. Strong long-term hold candidate."
    elif dividend_yield >= 3.5:
        div_rating = "ATTRACTIVE"
        div_advice = "Good yield available. Consider accumulating on price dips."
    else:
        div_rating = "EXPENSIVE"
        div_advice = "Yield is currently low. Wait for price correction for better entry."
    
    div_reasons = [
        f"Current yield: {dividend_yield}% vs market average.",
        f"Price is {'close to' if current_price <= buy_zone_max else 'above'} best entry zone."
    ]
    
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
            "current_yield_percent": f"{dividend_yield:.2f}",
            "max_yield_percent": f"{max_yield_possible:.2f}",
            "best_buy_zone": best_buy_zone,
            "price_upside_percent": f"{price_upside:.1f}",
            "reasons": div_reasons,
            "advice": div_advice
        }
    }

def main():
    print("🔄 Starting stock analysis...")
    results = []
    
    for symbol, name in STOCKS.items():
        print(f"  → Analyzing {symbol}: {name}")
        try:
            data = analyze_stock(symbol, name)
            results.append(data)
        except Exception as e:
            print(f"  ⚠️ Error analyzing {symbol}: {e}")
    
    output = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_stocks": len(results),
        "stock_list": results
    }
    
    # Ensure output folder exists
    os.makedirs("output", exist_ok=True)
    
    # Save JSON output
    with open("output/hasil_analisa.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Done! Results saved to: output/hasil_analisa.json")
    print(f"📊 Total stocks analyzed: {len(results)}")

if __name__ == "__main__":
    main()
