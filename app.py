import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="AI Stock Leaderboard", layout="wide")
st.title("🏆 AI Stock Leaderboard (Yahoo Finance)")

# ----------------------------
# STOCK UNIVERSE (you can edit this list)
# ----------------------------
STOCK_LIST = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "META", "TSLA", "NFLX", "AMD", "INTC",
    "JPM", "V", "MA", "DIS", "KO"
]

# ----------------------------
# DATA FETCH
# ----------------------------
def get_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="6mo")
        return info, hist
    except Exception:
        return None, None


# ----------------------------
# FEATURES
# ----------------------------
def compute_features(info, hist):
    if hist is None or hist.empty:
        return None

    start = hist["Close"].iloc[0]
    end = hist["Close"].iloc[-1]

    price_growth = (end - start) / start
    volatility = hist["Close"].pct_change().std()

    return {
        "price_growth": price_growth,
        "volatility": volatility,
        "profit_margin": info.get("profitMargins", 0) or 0,
        "earnings_growth": info.get("earningsQuarterlyGrowth", 0) or 0,
        "dividend_yield": info.get("dividendYield", 0) or 0,
    }


# ----------------------------
# AI SCORE MODEL
# ----------------------------
def ai_score(f):
    if not f:
        return 0

    score = 0
    score += f["price_growth"] * 45
    score += f["earnings_growth"] * 25
    score += f["profit_margin"] * 20
    score += f["dividend_yield"] * 10
    score -= f["volatility"] * 50

    score = 50 + score * 10
    return round(max(0, min(100, score)), 2)


# ----------------------------
# BUILD LEADERBOARD
# ----------------------------
def build_leaderboard():
    results = []

    for ticker in STOCK_LIST:
        info, hist = get_data(ticker)

        if not hist is None and not hist.empty:
            features = compute_features(info, hist)
            score = ai_score(features)

            results.append({
                "Ticker": ticker,
                "AI Score": score,
                "6M Growth %": features["price_growth"] * 100,
                "Volatility": features["volatility"]
            })

    df = pd.DataFrame(results)
    df = df.sort_values("AI Score", ascending=False)

    return df


# ----------------------------
# USER INPUT
# ----------------------------
st.subheader("📊 Top Stocks Leaderboard")

if st.button("Generate Leaderboard"):
    with st.spinner("Analyzing stocks..."):
        leaderboard = build_leaderboard()

        st.success("Done!")

        st.dataframe(
            leaderboard,
            use_container_width=True
        )

        # ----------------------------
        # TOP 5 CHART
        # ----------------------------
        st.subheader("🏆 Top 5 Stocks")

        top5 = leaderboard.head(5)

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=top5["Ticker"],
            y=top5["AI Score"],
            name="AI Score"
        ))

        st.plotly_chart(fig, use_container_width=True)


# ----------------------------
# INDIVIDUAL STOCK VIEW
# ----------------------------
st.subheader("🔍 Single Stock Analyzer")

ticker = st.text_input("Enter ticker", "AAPL")

if ticker:
    info, hist = get_data(ticker)

    if info and hist is not None and not hist.empty:

        st.write(info.get("longName", ticker))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist["Close"],
            mode="lines"
        ))
        st.plotly_chart(fig, use_container_width=True)

        features = compute_features(info, hist)
        score = ai_score(features)

        st.metric("AI Score", f"{score}/100")
