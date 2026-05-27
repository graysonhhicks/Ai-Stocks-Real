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
# SAFE API KEY HANDLING (FIXED)
# ----------------------------

API_KEY = None

# 1. Try Streamlit secrets (safe access)
try:
    API_KEY = st.secrets.get("FMP_API_KEY", None)
except Exception:
    API_KEY = None

# 2. Try environment variable
if not API_KEY:
    API_KEY = os.getenv("FMP_API_KEY")

# 3. LAST RESORT: user input in sidebar (FIX THAT BREAKS EVERYTHING)
if not API_KEY:
    API_KEY = st.sidebar.text_input(
        "Enter FMP API Key",
        type="password",
        help="Get your key from financialmodelingprep.com"
    )

# ----------------------------
# FMP DATA FUNCTION (SAFE)
# ----------------------------
def get_fmp_data(ticker):
    if not API_KEY:
        return None

    url = f"https://financialmodelingprep.com/api/v3/key-metrics/{ticker}?apikey={API_KEY}"

    try:
        r = requests.get(url, timeout=10)
        data_json = r.json()

        # API sometimes returns dict instead of list on error
        if not isinstance(data_json, list) or len(data_json) == 0:
            return None

        data = data_json[0]

        return {
            "revenueGrowth": data.get("revenueGrowth", 0) * 100,
            "roe": data.get("roe", 0) * 100,
            "debtToEquity": data.get("debtToEquity", 0),
        }

    except Exception:
        return None


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
# USER INPUT
# ----------------------------
ticker = st.text_input("Enter Stock Ticker", "AAPL")

if ticker:

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
    # FMP METRICS
    # ----------------------------
    fmp = get_fmp_data(ticker)

    if fmp:
        st.subheader("📊 Fundamental Metrics (FMP)")
        col1, col2, col3 = st.columns(3)

        col1.metric("Revenue Growth %", f"{fmp['revenueGrowth']:.2f}%")
        col2.metric("ROE %", f"{fmp['roe']:.2f}%")
        col3.metric("Debt/Equity", f"{fmp['debtToEquity']:.2f}")

    else:
        st.warning(
            "FMP data not available. "
            "Add your API key in the sidebar or Streamlit secrets."
        )
