# 📊 Stock Volume Profile Analyzer

> Identify key support & resistance levels from real volume distribution — for any US stock, completely free.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## What is Volume Profile?

Volume Profile shows **how much volume was traded at each price level** over a given period. Unlike standard volume bars (which show volume over time), this reveals *where* the market has the most activity — forming natural support and resistance zones.

This tool is inspired by [Glassnode's URPD chart](https://glassnode.com) for Bitcoin, adapted for US equities using free data.

**Key concepts:**

| Term | Meaning |
|------|---------|
| **POC** (Point of Control) | Price level with the highest traded volume — strongest magnet |
| **Value Area (VA)** | Price range containing 70% of total volume |
| **VAH / VAL** | Value Area High / Low — key boundary levels |
| **Volume Peaks** | Local high-volume nodes — act as support or resistance |

---

## Features

- **1H & 4H** timeframes (60-day lookback)
- Interactive **Plotly** charts with zoom & hover
- Automatic detection of **top 6 volume peaks**
- Value Area shading (green zone = 70% of volume)
- Clean dark-mode UI built with **Streamlit**
- Zero API key required — uses Yahoo Finance

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/Hiaty/stock-volume-profile.git
cd stock-volume-profile

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Usage

1. Enter any US stock ticker (e.g. `SOFI`, `NVDA`, `AAPL`)
2. Click **Analyze**
3. Read the chart:
   - **Yellow dashed line** = current price
   - **Red dashed line** = POC
   - **Green shaded area** = Value Area (70% of volume)
   - **Blue labels** = volume peaks with % distance from current price

---

## How It Works

1. Downloads 60 days of 1-hour OHLCV data via `yfinance`
2. Aggregates to 4H by resampling
3. Distributes each candle's volume evenly across its High-Low price range
4. Bins all volume into 80 price levels
5. Identifies peaks using `scipy.signal.find_peaks` with prominence filtering

---

## Example Output

```
SOFI  [1H]  Current: $15.14
────────────────────────────
POC         $18.76   ← highest volume node
Value Area  $16.53 ~ $22.87  (70% of volume)

Key Peaks:
  $15.22   -0.6%   Support
  $17.64  -14.2%   Resistance
  $18.76  -19.3%   Resistance (POC)
  $21.19  -28.6%   Resistance
  $22.68  -33.3%   Resistance
  $26.60  -43.1%   Resistance
```

---

## Limitations

- Data is limited to **60 days** (Yahoo Finance free tier for 1H intervals)
- Volume is approximated by distributing each candle's volume uniformly across its price range (not tick-level data)
- For higher precision, consider [Polygon.io](https://polygon.io) tick data

---

## License

MIT — free to use, modify, and distribute.
