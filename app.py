import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="AI Stock Dashboard", layout="wide")
st.title("📊 AI Stock Intelligence Dashboard")

# ----------------------------
# STOCK UNIVERSE
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
        "beta": info.get("beta", 1) or 1,
        "sector": info.get("sector", "Unknown")
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
    score -= abs(f["beta"] - 1) * 10

    score = 50 + score * 10
    return round(max(0, min(100, score)), 2)


# ----------------------------
# PULSE METER (GREEN / ORANGE / RED)
# ----------------------------
def pulse(score):
    if score >= 70:
        return "🟢 STRONG BUY (Green Zone)"
    elif score >= 40:
        return "🟠 HOLD / NEUTRAL (Orange Zone)"
    else:
        return "🔴 WEAK / RISKY (Red Zone)"


# ----------------------------
# 8-SENTENCE AI SUMMARY (simple template-based)
# ----------------------------
def summarize_stock(ticker, f, score):
    if not f:
        return "No data available."

    direction = "positive" if score > 55 else "mixed" if score > 40 else "negative"

    summary = f"""
1. {ticker} shows a {direction} performance trend based on its 6-month market behavior.  
2. The stock has a price growth of approximately {f['price_growth']*100:.2f}%, indicating momentum conditions.  
3. Earnings growth signals are {'strong' if f['earnings_growth'] > 0 else 'weak or inconsistent'}.  
4. Profit margins suggest {'efficient operations' if f['profit_margin'] > 0.1 else 'moderate profitability pressure'}.  
5. Volatility levels indicate {'stable movement' if f['volatility'] < 0.03 else 'higher-than-average risk exposure'}.  
6. Dividend yield contribution is {'meaningful' if f['dividend_yield'] > 0 else 'minimal or absent'}.  
7. Overall sentiment classification places the stock in a {pulse(score)} category.  
8. This evaluation reflects a combined momentum, risk, and fundamental scoring model.
"""
    return summary


# ----------------------------
# BUILD LEADERBOARD
# ----------------------------
def build_leaderboard():
    results = []

    for ticker in STOCK_LIST:
        info, hist = get_data(ticker)

        if hist is not None and not hist.empty:
            features = compute_features(info, hist)
            score = ai_score(features)

            results.append({
                "Ticker": ticker,
                "AI Score": score,
                "Pulse": pulse(score),
                "6M Growth %": features["price_growth"] * 100,
                "Volatility": features["volatility"]
            })

    df = pd.DataFrame(results)
    df = df.sort_values("AI Score", ascending=False)
    return df


# ----------------------------
# TOP PICKS SECTION (ABOVE SEARCH)
# ----------------------------
st.subheader("🏆 Top AI Stock Picks")

leaderboard = build_leaderboard()
top3 = leaderboard.head(3)

cols = st.columns(3)

for i, row in enumerate(top3.itertuples()):
    with cols[i]:
        st.metric(row.Ticker, f"{row._2}/100")
        st.write(row.Pulse)


st.divider()


# ----------------------------
# FULL LEADERBOARD
# ----------------------------
st.subheader("📊 Full Leaderboard")

st.dataframe(leaderboard, use_container_width=True)

st.divider()


# ----------------------------
# SEARCH BAR (BELOW TOP PICKS)
# ----------------------------
st.subheader("🔍 Stock Analyzer")

ticker = st.text_input("Enter Stock Ticker", "AAPL")

if ticker:
    info, hist = get_data(ticker)

    if info and hist is not None and not hist.empty:

        st.write(f"### {info.get('longName', ticker)}")

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
        st.write(pulse(score))

        st.subheader("🧠 AI Summary")
        st.write(summarize_stock(ticker, features, score))
