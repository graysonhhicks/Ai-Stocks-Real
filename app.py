import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="AI Stock Leaderboard", layout="wide")
st.title("📊 AI Stock Leaderboard (Yahoo Finance Only)")

# ----------------------------
# STOCK UNIVERSE
# ----------------------------
STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
    "TSLA", "NVDA", "NFLX", "AMD", "JPM",
    "V", "MA", "DIS", "PLTR", "INTC"
]

# ----------------------------
# GET DATA
# ----------------------------
@st.cache_data(ttl=3600)
def get_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")

        if hist is None or hist.empty:
            return None, None

        return stock.info, hist
    except:
        return None, None


# ----------------------------
# AI SCORE ENGINE
# ----------------------------
def compute_score(hist):
    close = hist["Close"]

    # 6-month return
    return_6m = (close.iloc[-1] - close.iloc[0]) / close.iloc[0]

    # volatility (risk penalty)
    volatility = close.pct_change().std()

    # momentum (recent trend)
    momentum = (close.iloc[-1] - close.iloc[-20]) / close.iloc[-20]

    # volume strength (proxy)
    vol_strength = hist["Volume"].mean() / hist["Volume"].max()

    # AI score formula (0–100)
    score = (
        (return_6m * 60) +
        (momentum * 40) -
        (volatility * 50) +
        (vol_strength * 10)
    ) * 100

    return max(0, min(100, score))


# ----------------------------
# COLOR PULSE METER
# ----------------------------
def pulse_color(score):
    if score >= 70:
        return "🟢 STRONG (Green Zone)"
    elif score >= 40:
        return "🟠 MODERATE (Orange Zone)"
    else:
        return "🔴 WEAK (Red Zone)"


# ----------------------------
# AI SUMMARY (8 SENTENCES)
# ----------------------------
def generate_summary(ticker, score, hist):
    close = hist["Close"]

    change = (close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100
    volatility = hist["Close"].pct_change().std() * 100

    trend = "upward" if close.iloc[-1] > close.mean() else "downward"

    summary = f"""
1. {ticker} shows a 6-month price change of {change:.2f}%.
2. The stock is currently trending in a {trend} direction.
3. Price stability is measured with a volatility of about {volatility:.2f}%.
4. The AI score model evaluates momentum, risk, and performance.
5. Current AI Score: {score:.2f}/100.
6. This score reflects combined return strength and volatility adjustment.
7. Higher scores indicate stronger growth potential under current trends.
8. Overall, {ticker} is classified as {pulse_color(score)}.
"""
    return summary


# ----------------------------
# BUILD LEADERBOARD
# ----------------------------
def build_leaderboard():
    rows = []

    for ticker in STOCKS:
        info, hist = get_data(ticker)

        if hist is None:
            continue

        score = compute_score(hist)

        rows.append({
            "Ticker": ticker,
            "AI Score": score
        })

    df = pd.DataFrame(rows).sort_values("AI Score", ascending=False)

    return df


# ----------------------------
# LEADERBOARD SECTION (TOP)
# ----------------------------
st.subheader("🏆 AI Score Leaderboard")

leaderboard = build_leaderboard()

st.dataframe(leaderboard, use_container_width=True)


# ----------------------------
# STOCK DETAIL VIEW
# ----------------------------
st.subheader("📈 Analyze a Stock")

ticker = st.text_input("Search Stock (e.g. AAPL, TSLA, NVDA)", "AAPL")

if ticker:
    info, hist = get_data(ticker)

    if hist is None:
        st.error("No data found for this ticker.")
    else:
        score = compute_score(hist)

        st.subheader(f"{ticker} Analysis")
        st.markdown(f"### {pulse_color(score)}")
        st.metric("AI Score", f"{score:.2f}/100")

        # Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist["Close"],
            mode="lines",
            name="Price"
        ))
        st.plotly_chart(fig, use_container_width=True)

        # Summary
        summary = generate_summary(ticker, score, hist)
        st.subheader("🧠 AI Analysis Summary (8 Sentences)")
        st.write(summary)
