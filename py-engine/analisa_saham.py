#!/usr/bin/env python3
"""
Script untuk menganalisa harga entry saham Amerika
Ticker: SO, ED, O, WRTG
Strategi: Swing Trading + Dividen Investing
Output: ../output/hasil_analisa.json
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from pathlib import Path

# Daftar saham yang akan dianalisa
TICKERS = ["SO", "ED", "O", "WRTG"]

# Path output — ke folder output di atas
OUTPUT_FILE = Path(__file__).parent.parent / "output" / "hasil_analisa.json"

# Buat folder output jika belum ada
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# === Fungsi Hitung Indikator Teknis ===
def hitung_rsi(data, periode=14):
    """Relative Strength Index: 0-30 = Oversold, 70-100 = Overbought"""
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=periode).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periode).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def hitung_macd(data):
    """Moving Average Convergence Divergence"""
    ema12 = data['Close'].ewm(span=12, adjust=False).mean()
    ema26 = data['Close'].ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line.iloc[-1], signal_line.iloc[-1]

def hitung_bollinger(data, periode=20):
    """Bollinger Bands untuk zona support/resistance"""
    sma = data['Close'].rolling(window=periode).mean()
    std = data['Close'].rolling(window=periode).std()
    upper = sma + (2 * std)
    lower = sma - (2 * std)
    return upper.iloc[-1], sma.iloc[-1], lower.iloc[-1]

# === Fungsi Analisa Saham ===
def analisa_saham(simbol):
    print(f"🔍 Menganalisa {simbol}...")
    
    try:
        ticker = yf.Ticker(simbol)
        
        # Ambil data harga 1 tahun terakhir
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        hist = ticker.history(start=start_date, end=end_date, auto_adjust=True)
        
        if len(hist) < 60:
            print(f"⚠️ Data tidak cukup untuk {simbol}")
            return None
        
        # Info dasar & dividen
        info = ticker.info
        nama = info.get('longName', simbol)
        dividen_yield = info.get('dividendYield', 0) * 100  # %
        payout_ratio = info.get('payoutRatio', 0) * 100 if info.get('payoutRatio') else None
        ex_div_date = info.get('exDividendDate', '')
        if isinstance(ex_div_date, (int, float)):
            ex_div_date = datetime.fromtimestamp(ex_div_date).strftime('%Y-%m-%d')
        
        # Harga saat ini & statistik
        harga_sekarang = round(hist['Close'].iloc[-1], 2)
        harga_tertinggi_52w = round(hist['High'].max(), 2)
        harga_terendah_52w = round(hist['Low'].min(), 2)
        
        # MA
        ma20 = round(hist['Close'].rolling(20).mean().iloc[-1], 2)
        ma50 = round(hist['Close'].rolling(50).mean().iloc[-1], 2)
        ma200 = round(hist['Close'].rolling(200).mean().iloc[-1], 2) if len(hist)>=200 else None
        
        # RSI
        rsi = round(hitung_rsi(hist).iloc[-1], 1)
        
        # MACD
        macd, signal = hitung_macd(hist)
        
        # Bollinger Bands
        bb_atas, bb_tengah, bb_bawah = hitung_bollinger(hist)
        
        # === Rekomendasi Entry ===
        zona_entry = round(bb_bawah * 1.01, 2)
        zona_aman_bawah = round(harga_terendah_52w * 1.02, 2)
        resistance = round(min(bb_atas, harga_tertinggi_52w * 0.95), 2)
        
        # Hitung potensi keuntungan
        potensi_gain = round(((resistance - zona_entry) / zona_entry) * 100, 2)
        
        # Penilaian kondisi
        kondisi = "NETRAL"
        alasan = []
        
        if rsi < 35 and harga_sekarang <= bb_tengah:
            kondisi = "KESMPATAN ENTRY"
            alasan.append("RSI rendah (zona jenuh jual)")
        elif rsi < 30:
            kondisi = "SANGAT BAGUS"
            alasan.append("RSI < 30, zona jenuh jual kuat")
        elif rsi > 70:
            kondisi = "HINDARI / TUNGGU"
            alasan.append("RSI > 70, jenuh beli")
        
        if harga_sekarang <= ma20 and ma50 > ma20:
            alasan.append("Harga di bawah MA20, potensi pantul")
        elif harga_sekarang > ma50 and ma50 > ma200:
            alasan.append("Tren naik terkonfirmasi")
        
        # Dividen
        dividen_cat = "Kurang Menarik"
        if dividen_yield > 6:
            dividen_cat = "SANGAT TINGGI ⚠️ (periksa keberlanjutan)"
        elif 4 <= dividen_yield <= 6:
            dividen_cat = "IDEAL ✅"
        elif 2 <= dividen_yield < 4:
            dividen_cat = "Cukup Bagus ✅"
        elif dividen_yield > 0:
            dividen_cat = "Rendah"
        
        hasil = {
            "simbol": simbol,
            "nama": nama,
            "analisa_di": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "harga_sekarang": harga_sekarang,
            "harga_52minggu": {
                "terendah": harga_terendah_52w,
                "tertinggi": harga_tertinggi_52w
            },
            "indikator": {
                "ma20": ma20,
                "ma50": ma50,
                "ma200": ma200,
                "rsi": rsi,
                "macd": round(macd, 4),
                "signal_line": round(signal, 4),
                "bollinger_bawah": round(bb_bawah, 2),
                "bollinger_tengah": round(bb_tengah, 2),
                "bollinger_atas": round(bb_atas, 2)
            },
            "dividen": {
                "yield_persen": round(dividen_yield, 2),
                "kategori": dividen_cat,
                "payout_ratio_persen": round(payout_ratio, 1) if payout_ratio else None,
                "ex_div_date": ex_div_date
            },
            "rekomendasi": {
                "zona_entry": zona_entry,
                "zona_aman_bawah": zona_aman_bawah,
                "zona_resistance": resistance,
                "potensi_gain_persen": potensi_gain,
                "kondisi_saat_ini": kondisi,
                "alasan": alasan,
                "saran": f"Target beli di ${zona_entry}, target jual di ${resistance} (+{potensi_gain}%). "
                         f"Dividen yield: {round(dividen_yield,2)}% — {dividen_cat}"
            }
        }
        return hasil
    
    except Exception as e:
        print(f"❌ Error analisa {simbol}: {e}")
        return None

# === Fungsi Utama ===
def main():
    print("=" * 50)
    print("📊 ANALISA SAHAM AMERIKA — SWING & DIVIDEN")
    print("=" * 50)
    
    semua_hasil = []
    for ticker in TICKERS:
        res = analisa_saham(ticker)
        if res:
            semua_hasil.append(res)
    
    # Simpan ke JSON
    output = {
        "dibuat_pada": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "jumlah_saham": len(semua_hasil),
        "daftar_saham": semua_hasil
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Selesai! Hasil disimpan di: {OUTPUT_FILE.resolve()}")
    print(f"📋 Total dianalisa: {len(semua_hasil)} saham")

if __name__ == "__main__":
    main()
