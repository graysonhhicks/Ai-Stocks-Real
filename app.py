import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import plotly.graph_objects as go
import os

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="AI Stock Analyzer", layout="wide")
st.title("📊 AI Stock Analyzer")

# ----------------------------
# SAFE API KEY (NO CRASH VERSION)
# ----------------------------
API_KEY = os.getenv("FMP_API_KEY", "")

# ----------------------------
# YFINANCE DATA
# ----------------------------
def get_yfinance_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="6mo")
        return info, hist
    except Exception:
        return None, None

# ----------------------------
# FMP DATA (SAFE)
# ----------------------------
def get_fmp_data(ticker):
    if not API_KEY:
        return None

    url = f"https://financialmodelingprep.com/api/v3/key-metrics/{ticker}?apikey={API_KEY}"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        # Ensure it's a list
        if not isinstance(data, list) or len(data) == 0:
            return None

        item = data[0]

        return {
            "revenueGrowth": item.get("revenueGrowth", 0) * 100,
            "roe": item.get("roe", 0) * 100,
            "debtToEquity": item.get("debtToEquity", 0),
        }

    except Exception:
        return None

# ----------------------------
# USER INPUT
# ----------------------------
ticker = st.text_input("Enter Stock Ticker", "AAPL")

if ticker:

    # ----------------------------
    # YFINANCE SECTION
    # ----------------------------
    info, hist = get_yfinance_data(ticker)

    if info:
        st.subheader(info.get("longName", ticker))

    if hist is not None and not hist.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist["Close"],
            mode="lines",
            name="Close Price"
        ))
        st.plotly_chart(fig, use_container_width=True)

    # ----------------------------
    # FMP SECTION (OPTIONAL)
    # ----------------------------
    fmp = get_fmp_data(ticker)

    if fmp:
        st.subheader("📊 Fundamental Metrics (FMP)")

        col1, col2, col3 = st.columns(3)

        col1.metric("Revenue Growth %", f"{fmp['revenueGrowth']:.2f}%")
        col2.metric("ROE %", f"{fmp['roe']:.2f}%")
        col3.metric("Debt/Equity", f"{fmp['debtToEquity']:.2f}")

    else:
        st.info("FMP data not available (API key missing or request failed).")
