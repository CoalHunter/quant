# engine/quant_logic.py
import numpy as np
import pandas as pd
from config import SWING_PARAMS, DIVIDEND_PARAMS

def calculate_swing(hist, info):
    df = hist.copy()
    df['MA20'] = df['Close'].rolling(window=SWING_PARAMS['ma_short']).mean()
    df['MA50'] = df['Close'].rolling(window=SWING_PARAMS['ma_long']).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=SWING_PARAMS['rsi_period']).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=SWING_PARAMS['rsi_period']).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Volume Accumulation (OBV proxy)
    df['Vol_MA'] = df['Volume'].rolling(window=SWING_PARAMS['vol_ma']).mean()
    df['Accumulation'] = np.where(df['Volume'] > df['Vol_MA'] * 1.2, 1, 0)
    acc_score = min(100, int((df['Accumulation'].tail(20).sum() / 20) * 100))
    
    last_price = df['Close'].iloc[-1]
    ma50 = df['MA50'].iloc[-1]
    
    # Logic Sederhana: Buy if price near MA50 and RSI < 40
    status = "WAIT"
    if last_price <= ma50 * 1.02 and df['RSI'].iloc[-1] < 45:
        status = "BUY"
        
    return {
        "status": status,
        "entry_zone": [round(ma50 * 0.98, 2), round(ma50, 2)],
        "target_price": round(last_price * 1.10, 2), # 10% target
        "stop_loss": round(ma50 * 0.94, 2),
        "timeframe": "3-6 Weeks",
        "accumulation_score": acc_score,
        "current_rsi": round(df['RSI'].iloc[-1], 2)
    }

def calculate_dividend(info, hist):
    yield_pct = info.get('dividendYield', 0) * 100
    payout = info.get('payoutRatio', 0) * 100
    
    # Filter Dividend Trap
    sector = info.get('sector', '')
    max_payout = DIVIDEND_PARAMS['max_payout_reit'] if sector == 'Real Estate' else DIVIDEND_PARAMS['max_payout_utility']
    
    is_safe = payout < max_payout
    last_price = hist['Close'].iloc[-1]
    safe_entry = round(last_price * (1 - DIVIDEND_PARAMS['discount_safe_entry']), 2)
    
    return {
        "status": "ACCUMULATE" if is_safe and yield_pct > 4.0 else "HOLD",
        "safe_entry": safe_entry,
        "dividend_yield": round(yield_pct, 2),
        "payout_ratio": round(payout, 2),
        "ex_dividend_date": info.get('exDividendDate', 'N/A'),
        "frequency": "Monthly" if info.get('ticker') == 'O' else "Quarterly",
        "is_safe_from_trap": is_safe
  }
