"""
Stock Volume Profile — Streamlit Web App
Run: streamlit run app.py
"""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core import analyze

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Volume Profile Analyzer",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px 16px;
        text-align: center;
    }
    .metric-label { color: #8b949e; font-size: 12px; margin-bottom: 4px; }
    .metric-value { color: #e6edf3; font-size: 20px; font-weight: 600; }
    .tag-support  { color: #3fb950; font-size: 11px; }
    .tag-resist   { color: #f85149; font-size: 11px; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────
st.title("📊 Volume Profile Analyzer")
st.caption("Identify key support & resistance levels from real volume distribution · Powered by yfinance")

# ── Input ─────────────────────────────────────────────────
col_input, col_btn, col_spacer = st.columns([2, 1, 5])
with col_input:
    ticker = st.text_input("Ticker Symbol", value="SOFI", placeholder="AAPL, NVDA, TSLA…").upper().strip()
with col_btn:
    st.write("")
    run = st.button("Analyze", type="primary", use_container_width=True)

if not run:
    st.info("Enter a US stock ticker and click **Analyze** to generate the Volume Profile.")
    st.stop()

# ── Fetch & analyze ────────────────────────────────────────
with st.spinner(f"Fetching {ticker} data (60 days)…"):
    try:
        data = analyze(ticker)
    except Exception as e:
        st.error(str(e))
        st.stop()

cur = data["1H"]["current"]
poc_1h = data["1H"]["poc"]
val_1h = data["1H"]["val"]
vah_1h = data["1H"]["vah"]

# ── Top metrics ────────────────────────────────────────────
st.divider()
m1, m2, m3, m4, m5, m6 = st.columns(6)
def metric(col, label, value, sub=None, color="#e6edf3"):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color}">{value}</div>
            {"<div style='color:#8b949e;font-size:11px'>" + sub + "</div>" if sub else ""}
        </div>""", unsafe_allow_html=True)

pct_to_poc = (poc_1h - cur) / cur * 100
metric(m1, "Current Price",  f"${cur:.2f}",      color="#f0c040")
metric(m2, "POC (1H)",       f"${poc_1h:.2f}",   sub=f"{pct_to_poc:+.1f}% from now", color="#ff7b72")
metric(m3, "Value Area Low", f"${val_1h:.2f}",   color="#3fb950")
metric(m4, "Value Area High",f"${vah_1h:.2f}",   color="#3fb950")
metric(m5, "VA Width",       f"${vah_1h-val_1h:.2f}", sub="70% of volume", color="#79c0ff")
ma100_val = data["ma"].get("ma100", 0) or 0
ma200_val = data["ma"].get("ma200", 0) or 0
ma100_pct = (cur - ma100_val) / ma100_val * 100 if ma100_val else 0
metric(m6, "MA100(D) / MA200(D)",
       f"${ma100_val:.2f}",
       sub=f"MA200 ${ma200_val:.2f}  ({ma100_pct:+.1f}%)",
       color="#79c0ff")
st.write("")

# ── Charts ─────────────────────────────────────────────────
BG      = "#0d1117"
PANEL   = "#161b22"
GRID    = "#21262d"

def build_chart(info: dict, label: str, ma: dict = None):
    df      = info["df"]
    centers = info["centers"]
    vp      = info["vp"]
    poc     = info["poc"]
    val     = info["val"]
    vah     = info["vah"]
    peaks   = info["peaks"]
    cur     = info["current"]

    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.72, 0.28],
        shared_yaxes=True,
        horizontal_spacing=0.01,
    )

    # Moving Averages (日线级别，画水平线)
    ma_data = ma or {}
    ma_config = [
        ("ma20",  "MA20",  "#f0c040", 1.0),
        ("ma50",  "MA50",  "#ff7b72", 1.0),
        ("ma100", "MA100", "#79c0ff", 1.4),
        ("ma200", "MA200", "#bc8cff", 1.4),
    ]
    for key, name, color, width in ma_config:
        v = ma_data.get(key)
        if v is None:
            continue
        fig.add_hline(y=v, line_color=color, line_dash="dot",
                      line_width=width, row=1, col=1,
                      annotation_text=f"{name} ${v:.2f}",
                      annotation_font=dict(color=color, size=9),
                      annotation_position="right")

    # Price line (on top of MAs)
    fig.add_trace(go.Scatter(
        x=list(range(len(df))),
        y=df["Close"].values,
        mode="lines",
        line=dict(color="#58a6ff", width=1.2),
        name="Close",
        hovertemplate="%{y:.2f}<extra></extra>",
    ), row=1, col=1)

    # Value Area shading
    fig.add_hrect(y0=val, y1=vah, fillcolor="#238636", opacity=0.10,
                  layer="below", line_width=0, row=1, col=1)
    fig.add_hrect(y0=val, y1=vah, fillcolor="#238636", opacity=0.10,
                  layer="below", line_width=0, row=1, col=2)

    # POC & current price lines
    for y, color, dash, name in [
        (poc, "#ff7b72", "dash",  f"POC ${poc:.2f}"),
        (cur, "#f0c040", "dot",   f"NOW ${cur:.2f}"),
        (vah, "#3fb950", "dashdot", f"VAH ${vah:.2f}"),
        (val, "#3fb950", "dashdot", f"VAL ${val:.2f}"),
    ]:
        for col in [1, 2]:
            fig.add_hline(y=y, line_color=color, line_dash=dash,
                          line_width=1.4, row=1, col=col)

    # VP bars
    bar_h  = (centers[1] - centers[0]) * 0.85
    colors = ["#2ea043" if val <= p <= vah else "#30363d" for p in centers]
    fig.add_trace(go.Bar(
        x=vp, y=centers,
        orientation="h",
        width=bar_h,
        marker_color=colors,
        name="Volume",
        hovertemplate="$%{y:.2f}  vol: %{x:,.0f}<extra></extra>",
    ), row=1, col=2)

    # Peak markers on VP
    for price, pvol in peaks:
        diff = (cur - price) / cur * 100
        fig.add_trace(go.Scatter(
            x=[pvol * 1.05], y=[price],
            mode="text",
            text=[f"  ${price:.2f} ({diff:+.1f}%)"],
            textfont=dict(color="#79c0ff", size=10),
            showlegend=False,
            hoverinfo="skip",
        ), row=1, col=2)

    # X-axis ticks (dates)
    step = max(1, len(df) // 8)
    tick_vals = list(range(0, len(df), step))
    tick_text = [df.index[i].strftime("%m/%d") for i in tick_vals]

    fig.update_layout(
        height=500,
        paper_bgcolor=BG,
        plot_bgcolor=PANEL,
        font=dict(color="#c9d1d9", size=11),
        title=dict(text=f"<b>{ticker}  {label}</b>", font=dict(size=14, color="white"), x=0.01),
        showlegend=True,
        legend=dict(
            orientation="h", x=0.01, y=1.08,
            font=dict(size=10, color="#c9d1d9"),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=10, r=10, t=55, b=30),
        xaxis=dict(
            tickvals=tick_vals, ticktext=tick_text,
            gridcolor=GRID, zeroline=False, color="#8b949e",
        ),
        xaxis2=dict(gridcolor=GRID, zeroline=False, color="#8b949e",
                    title=dict(text="Volume", font=dict(size=10))),
        yaxis=dict(gridcolor=GRID, zeroline=False, color="#8b949e",
                   title=dict(text="Price (USD)", font=dict(size=10))),
    )
    return fig

tab1h, tab4h = st.tabs(["1H — 60 Days", "4H — 60 Days"])

with tab1h:
    st.plotly_chart(build_chart(data["1H"], "1H", data["ma"]), use_container_width=True)

with tab4h:
    st.plotly_chart(build_chart(data["4H"], "4H", data["ma"]), use_container_width=True)

# ── Key levels table ────────────────────────────────────────
st.subheader("Key Levels")
tcol1, tcol2 = st.columns(2)

for col, label in [(tcol1, "1H"), (tcol2, "4H")]:
    info  = data[label]
    peaks = info["peaks"]
    cur   = info["current"]
    with col:
        st.markdown(f"**{label} Peaks**")
        rows = []
        for price, _ in reversed(peaks):
            diff = (price - cur) / cur * 100
            tag  = "🔴 Resistance" if price > cur else "🟢 Support"
            rows.append({"Price": f"${price:.2f}", "vs Now": f"{diff:+.1f}%", "Type": tag})
        st.dataframe(rows, use_container_width=True, hide_index=True)

# ── Footer ─────────────────────────────────────────────────
st.divider()
st.caption("Data via Yahoo Finance · 365-day lookback · 1H bars aggregated to 4H · Value Area = 70% of total volume")
