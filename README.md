# Quant — US Domestic Infrastructure Dashboard

Dasbor analisis kuantitatif saham infrastruktur domestik Amerika Serikat. Fokus pada analisis teknikal (Swing Trading) dan fundamental (Dividend Play) dengan deteksi akumulasi institusional.

🔗 **Live Demo:** https://CoalHunter.github.io/quant/

---

## 🎯 Fokus Proyek

Proyek ini **hanya** menganalisis 4 emiten infrastruktur murni domestik AS:

| Ticker | Nama Perusahaan | Sektor | Frekuensi Dividen |
|--------|----------------|--------|-------------------|
| **SO** | Southern Company | Utilities | Kuartalan |
| **ED** | Consolidated Edison | Utilities | Kuartalan |
| **O**  | Realty Income Corp | Real Estate (REIT) | Bulanan |
| **WTRG** | Essential Utilities | Utilities | Kuartalan |

### 🛡️ Filter Geopolitik Mutlak
Keempat emiten di atas dipilih karena **100% beroperasi domestik di AS** (Utilities & Domestic REITs). Tidak ada eksposur ke konglomerasi multinasional, pusat riset eksternal, atau afiliasi geopolitik kontroversial.

---

## ✨ Fitur Utama

### 📈 Swing Trading
- Entry Zone berbasis **MA50** dan **Support Dinamis**
- Target Jual berbasis **Fibonacci Extension** & resistance historis
- Stop Loss terukur
- Timeframe: 3-6 minggu
- Indikator **RSI (14)** untuk konfirmasi momentum

###  Dividend Play
- **Safe Entry** dengan diskon 3% dari harga terkini
- Filter **Dividend Trap** (Payout Ratio < 85% Utilities, < 95% REITs)
- Yield on Cost projection
- Tracking Ex-Dividend Date

###  Deteksi Akumulasi Bandar
- Analisis **Volume vs Volume MA (20 hari)**
- Scoring akumulasi 0-100%
- Deteksi unusual volume (>120% dari rata-rata)

---

## 🏗️ Arsitektur Proyek
