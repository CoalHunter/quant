#!/usr/bin/env python3
"""
Analisa Saham — SWING TRADING vs STRATEGI DIVIDEN
Ticker: SO, ED, O, WTRG
Output: ../output/hasil_analisa.json
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

TICKERS = ["SO", "ED", "O", "WTRG"]
OUTPUT_FILE = Path(__file__).parent.parent / "output" / "hasil_analisa.json"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════
# INDICATORS
# ═══════════════════════════════════════════════
def hitung_rsi(data, periode=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=periode).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periode).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def hitung_bollinger(data, periode=20):
    sma = data['Close'].rolling(window=periode).mean()
    std = data['Close'].rolling(window=periode).std()
    return sma.iloc[-1], (sma + 2*std).iloc[-1], (sma - 2*std).iloc[-1]


# ═══════════════════════════════════════════════
# ANALISIS SWING TRADING — Fokus Teknikal
# ═══════════════════════════════════════════════
def analisa_swing(harga_sekarang, bb_bawah, bb_tengah, bb_atas, rsi, ma20, ma50, terendah_52w, tertinggi_52w):
    zona_entry = round(max(bb_bawah, terendah_52w * 1.03), 2)
    resistance = round(min(bb_tengah, ma20), 2) if harga_sekarang < ma20 else round(min(bb_atas, tertinggi_52w * 0.92), 2)
    potensi_gain = round(((resistance - zona_entry) / zona_entry) * 100, 2)

    kondisi = "NETRAL"
    alasan = []
    if rsi < 35 and harga_sekarang <= bb_tengah:
        kondisi = "✅ ENTRY SWING"
        alasan.append("RSI rendah → potensi pantul ke atas")
    elif rsi < 30:
        kondisi = "🔥 ENTRY KUAT"
        alasan.append("RSI < 30, zona jenuh jual kuat")
    elif rsi > 70:
        kondisi = "⏳ TUNGGU TURUN"
        alasan.append("RSI tinggi, jangan kejar")

    if harga_sekarang > ma50:
        alasan.append("Harga di atas MA50 → tren naik")
    elif harga_sekarang < ma20 and harga_sekarang < ma50:
        alasan.append("Di bawah MA20/50 → hati-hati")

    return {
        "zona_entry": zona_entry,
        "target_jual": resistance,
        "potensi_gain_persen": potensi_gain,
        "kondisi": kondisi,
        "alasan": alasan,
        "saran": f"Beli di ${zona_entry}, jual di ${resistance} → +{potensi_gain}%. RSI saat ini: {rsi}"
    }


# ═══════════════════════════════════════════════
# ANALISIS DIVIDEN — Harga Terendah + Yield Maksimal
# ═══════════════════════════════════════════════
def analisa_dividen(harga_sekarang, terendah_52w, tertinggi_52w, dividen_yield):
    # Zona beli terbaik = sedikit di atas terendah 52 minggu → YIELD MAKSIMAL
    zona_beli_terbaik = round(terendah_52w * 1.015, 2)
    zona_beli_wajar = round(((terendah_52w * 1.08) + (tertinggi_52w * 0.60)) / 2, 2)

    dividen_tahunan = round((dividen_yield / 100) * zona_beli_terbaik, 2) if dividen_yield > 0 else 0
    yield_terbaik = round((dividen_yield / zona_beli_terbaik) * harga_sekarang, 2) if zona_beli_terbaik > 0 else dividen_yield

    target_jangka_panjang = round(tertinggi_52w * 0.60, 2)
    potensi_naik = round(((target_jangka_panjang - zona_beli_terbaik) / zona_beli_terbaik) * 100, 2)

    penilaian = "CUKUP"
    if yield_terbaik >= 5.5:
        penilaian = "🌟 SANGAT MENARIK"
    elif 4.0 <= yield_terbaik < 5.5:
        penilaian = "✅ BAGUS"
    elif 3.0 <= yield_terbaik < 4.0:
        penilaian = "⚠️ CUKUP"
    elif yield_terbaik < 2.5:
        penilaian = "⏳ KURANG MENARIK"

    alasan = []
    if zona_beli_terbaik < harga_sekarang:
        diskon = round(((harga_sekarang - zona_beli_terbaik) / harga_sekarang) * 100, 1)
        alasan.append(f"Saat ini terlalu mahal. Tunggu turun ~{diskon}% lagi")
    else:
        alasan.append(f"Sudah di zona bagus, yield bisa mencapai {round(dividen_yield,2)}%+")

    alasan.append(f"Zona terbaik di ${zona_beli_terbaik} — dekat terendah 52 minggu")
    alasan.append(f"Target jangka panjang: ${target_jangka_panjang} (+{potensi_naik}%)")

    return {
        "zona_beli_terbaik": zona_beli_terbaik,
        "zona_beli_wajar": zona_beli_wajar,
        "target_jangka_panjang": target_jangka_panjang,
        "yield_saat_ini_persen": round(dividen_yield, 2),
        "yield_maksimal_persen": round(yield_terbaik, 2),
        "dividen_tahunan_per_saham": dividen_tahunan,
        "potensi_naik_harga_persen": potensi_naik,
        "penilaian": penilaian,
        "alasan": alasan,
        "saran": f"✅ BELI di ${zona_beli_terbaik} → Yield ~{round(dividen_yield,2)}%. Tahan untuk dividen + kenaikan harga ke ${target_jangka_panjang}"
    }


# ═══════════════════════════════════════════════
# PROSES PER SAHAM
# ═══════════════════════════════════════════════
def proses_saham(simbol):
    print(f"🔍 Memproses {simbol}...")
    time.sleep(0.3)

    try:
        ticker = yf.Ticker(simbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        hist = ticker.history(start=start_date, end=end_date, auto_adjust=True, timeout=20)

        if len(hist) < 60:
            print(f"⚠️ Data tidak cukup untuk {simbol}")
            return None

        info = ticker.info
        nama = info.get('longName', simbol)

        harga_sekarang = round(hist['Close'].iloc[-1], 2)
        terendah_52w = round(hist['Low'].min(), 2)
        tertinggi_52w = round(hist['High'].max(), 2)

        ma20 = round(hist['Close'].rolling(20).mean().iloc[-1], 2)
        ma50 = round(hist['Close'].rolling(50).mean().iloc[-1], 2)
        rsi = round(hitung_rsi(hist).iloc[-1], 1)
        bb_tengah, bb_atas, bb_bawah = hitung_bollinger(hist)

        dividen_yield = info.get('dividendYield', 0) * 100
        ex_div_date = info.get('exDividendDate', '')
        if isinstance(ex_div_date, (int, float)):
            ex_div_date = datetime.fromtimestamp(ex_div_date).strftime('%Y-%m-%d')

        swing = analisa_swing(harga_sekarang, bb_bawah, bb_tengah, bb_atas, rsi, ma20, ma50, terendah_52w, tertinggi_52w)
        dividen = analisa_dividen(harga_sekarang, terendah_52w, tertinggi_52w, dividen_yield)

        return {
            "simbol": simbol,
            "nama": nama,
            "harga_sekarang": harga_sekarang,
            "harga_52minggu": {"terendah": terendah_52w, "tertinggi": tertinggi_52w},
            "indikator": {"rsi": rsi, "ma20": ma20, "ma50": ma50},
            "dividen_info": {"yield_persen": round(dividen_yield, 2), "ex_div_date": ex_div_date},
            "swing": swing,
            "dividen": dividen
        }
    except Exception as e:
        print(f"❌ Error {simbol}: {e}")
        return None


# ═══════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════
def main():
    print("=" * 60)
    print("📊 SWING TRADING vs STRATEGI DIVIDEN")
    print("=" * 60)

    hasil = [ps for t in TICKERS if (ps := proses_saham(t))]

    output = {
        "dibuat_pada": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "jumlah_saham": len(hasil),
        "daftar_saham": hasil
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Selesai! → {OUTPUT_FILE.resolve()}")
    print(f"📋 Total: {len(hasil)} saham")


if __name__ == "__main__":
    main()
