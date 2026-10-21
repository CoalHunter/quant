# engine/config.py
import sys

# FILTER GEOPOLITIK & ENTITAS FOKUS (Murni Domestik AS)
TICKERS = ['SO', 'ED', 'O', 'WTRG']
ALLOWED_SECTORS = ['Utilities', 'Real Estate']

def validate_tickers(tickers):
    for t in tickers:
        if t not in TICKERS:
            print(f"ERROR: Ticker {t} ditolak. Hanya {TICKERS} yang diizinkan.")
            sys.exit(1)

# PARAMETER STRATEGI
SWING_PARAMS = {
    'ma_short': 20,
    'ma_long': 50,
    'rsi_period': 14,
    'vol_ma': 20
}

DIVIDEND_PARAMS = {
    'max_payout_utility': 0.85,
    'max_payout_reit': 0.95,
    'discount_safe_entry': 0.03
}
