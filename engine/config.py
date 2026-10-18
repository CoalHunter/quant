# engine/config.py
import sys

# ENTITAS SAHAM FOKUS (Murni Domestik AS: Utilities & REITs)
TICKERS = ['SO', 'ED', 'O', 'WTRG']

# Validasi Ketat: Mencegah injeksi ticker eksternal
ALLOWED_SECTORS = ['Utilities', 'Real Estate']

def validate_tickers(tickers):
    for t in tickers:
        if t not in TICKERS:
            print(f"ERROR: Ticker {t} tidak diizinkan. Hanya {TICKERS} yang valid.")
            sys.exit(1)

# Parameter Strategi
SWING_PARAMS = {
    'ma_short': 20,
    'ma_long': 50,
    'rsi_period': 14,
    'vol_ma': 20
}

DIVIDEND_PARAMS = {
    'max_payout_utility': 0.80,
    'max_payout_reit': 0.90,
    'discount_to_intrinsic': 0.05 # 5% discount untuk safe entry
}
