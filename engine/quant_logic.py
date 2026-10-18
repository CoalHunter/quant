# engine/quant_logic.py
import numpy as np
import pandas as pd
from config import SWING_PARAMS, DIVIDEND_PARAMS

def calculate_swing(hist, info):
    default = {
        "status": "WAIT", "entry_zone": [0, 0], "target_price": 0,
        "stop_loss": 0, "timeframe": "N/A", "accumulation_score": 0, "current_rsi": 0
    }
    
    try:
        if hist.empty or len(hist) < 50 or 'Close' not in hist.columns:
            return default
        
        df = hist.copy()
        
        # Normalisasi kolom (beberapa sumber pakai huruf kecil)
        df.columns = [c.capitalize() for c in df.columns]
        
        df['MA20'] = df['Close'].rolling(window=SWING_PARAMS['ma_short']).mean()
        df['MA50'] = df['Close'].rolling(window=SWING_PARAMS['ma_long']).mean()
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=SWING_PARAMS['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=SWING_PARAMS['rsi_period']).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        df['Vol_MA'] = df['Volume'].rolling(window=SWING_PARAMS['vol_ma']).mean()
        df['Accumulation'] = np.where(df['Volume'] > df['Vol_MA'] * 1.2, 1, 0)
        acc_score = min(100, int((df['Accumulation'].tail(20).sum() / 20) * 100))
        
        last_price = float(df['Close'].iloc[-1])
        ma50 = float(df['MA50'].iloc[-1]) if not pd.isna(df['MA50'].iloc[-1]) else last_price
        rsi_val = float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else 50
        
        status = "WAIT"
        if last_price <= ma50 * 1.02 and rsi_val < 45:
            status = "BUY"
            
        return {
            "status": status,
            "entry_zone": [round(ma50 * 0.98, 2), round(ma50, 2)],
            "target_price": round(last_price * 1.10, 2),
            "stop_loss": round(ma50 * 0.94, 2),
            "timeframe": "3-6 Weeks",
            "accumulation_score": acc_score,
            "current_rsi": round(rsi_val, 2)
        }
    except Exception as e:
        print(f"  Error calculate_swing: {e}")
        return default

def calculate_dividend(info, hist):
    default = {
        "status": "HOLD", "safe_entry": 0, "dividend_yield": 0,
        "payout_ratio": 0, "ex_dividend_date": "N/A",
        "frequency": "N/A", "is_safe_from_trap": False
    }
    
    try:
        if hist.empty or 'Close' not in hist.columns:
            return default
        
        yield_pct = float(info.get('dividendYield') or 0) * 100
        payout = float(info.get('payoutRatio') or 0) * 100
        
        sector = info.get('sector', '')
        max_payout = DIVIDEND_PARAMS['max_payout_reit'] if sector == 'Real Estate' else DIVIDEND_PARAMS['max_payout_utility']
        
        is_safe = payout < max_payout if payout > 0 else True
        last_price = float(hist['Close'].iloc[-1])
        safe_entry = round(last_price * (1 - DIVIDEND_PARAMS['discount_safe_entry']), 2)
        
        ex_date = info.get('exDividendDate', 'N/A')
        if isinstance(ex_date, (int, float)):
            try:
                ex_date = pd.Timestamp(ex_date, unit='s').strftime('%Y-%m-%d')
            except:
                ex_date = 'N/A'
        
        return {
            "status": "ACCUMULATE" if is_safe and yield_pct > 4.0 else "HOLD",
            "safe_entry": safe_entry,
            "dividend_yield": round(yield_pct, 2),
            "payout_ratio": round(payout, 2),
            "ex_dividend_date": ex_date,
            "frequency": "Monthly" if info.get('ticker') == 'O' else "Quarterly",
            "is_safe_from_trap": is_safe
        }
    except Exception as e:
        print(f"  Error calculate_dividend: {e}")
        return default
