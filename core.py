"""
Volume Profile core logic — data fetching & calculation
"""

import numpy as np
import pandas as pd
import yfinance as yf

NUM_BINS    = 80
VA_PCT      = 0.70
TOP_N_PEAKS = 6


def fetch_data(ticker: str, period: str = "365d"):
    t = yf.Ticker(ticker)
    df_1h = t.history(period=period, interval="1h")
    if df_1h.empty:
        raise ValueError(f"Cannot fetch data for '{ticker}'. Check the ticker symbol.")
    df_1h.index = pd.to_datetime(df_1h.index)
    df_1h = df_1h[["Open", "High", "Low", "Close", "Volume"]].dropna()
    df_4h = df_1h.resample("4h").agg(
        {"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}
    ).dropna()
    return df_1h, df_4h


def build_volume_profile(df: pd.DataFrame, num_bins: int = NUM_BINS):
    lo_all = df["Low"].min()
    hi_all = df["High"].max()
    bins = np.linspace(lo_all, hi_all, num_bins + 1)
    centers = (bins[:-1] + bins[1:]) / 2
    vp = np.zeros(num_bins)
    for _, row in df.iterrows():
        lo, hi, vol = row["Low"], row["High"], row["Volume"]
        s = max(0, np.searchsorted(bins, lo, "left") - 1)
        e = min(num_bins, np.searchsorted(bins, hi, "right"))
        n = e - s
        if n > 0:
            vp[s:e] += vol / n
    return centers, vp


def find_poc(centers, vp):
    idx = np.argmax(vp)
    return centers[idx], idx


def find_value_area(centers, vp, poc_idx, va_pct=VA_PCT):
    total = vp.sum()
    target = total * va_pct
    lo = hi = poc_idx
    cur = vp[poc_idx]
    while cur < target:
        lo_ok = lo > 0
        hi_ok = hi < len(vp) - 1
        if not lo_ok and not hi_ok:
            break
        elif not lo_ok:
            hi += 1; cur += vp[hi]
        elif not hi_ok:
            lo -= 1; cur += vp[lo]
        elif vp[lo - 1] >= vp[hi + 1]:
            lo -= 1; cur += vp[lo]
        else:
            hi += 1; cur += vp[hi]
    return centers[lo], centers[hi]


def find_peaks(centers, vp, top_n=TOP_N_PEAKS):
    try:
        from scipy.signal import find_peaks as sp_peaks
        idxs, _ = sp_peaks(vp, prominence=vp.max() * 0.06, distance=3)
    except ImportError:
        idxs = []
    if len(idxs) == 0:
        idxs = [np.argmax(vp)]
    top = sorted(idxs, key=lambda i: vp[i], reverse=True)[:top_n]
    top.sort()
    return [(centers[i], vp[i]) for i in top]


def analyze(ticker: str, period: str = "365d"):
    """Return analysis dict for both timeframes."""
    df_1h, df_4h = fetch_data(ticker, period=period)
    result = {}
    for label, df in [("1H", df_1h), ("4H", df_4h)]:
        centers, vp  = build_volume_profile(df)
        poc, poc_idx = find_poc(centers, vp)
        val, vah     = find_value_area(centers, vp, poc_idx)
        peaks        = find_peaks(centers, vp)
        cur          = df["Close"].iloc[-1]
        result[label] = {
            "df": df,
            "centers": centers,
            "vp": vp,
            "poc": poc,
            "val": val,
            "vah": vah,
            "peaks": peaks,
            "current": cur,
        }
    return result
