import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

from ai_score import calculate_ai_score, rating, color

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="AI Stock Terminal",
    page_icon="📈",
    layout="wide"
)

# ---------------------------------------------------
# DARK MODE UI
# ---------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #0b0f19;
    color: white;
}

h1, h2, h3 {
    color: white;
}

[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1f2937;
    padding: 15px;
    border-radius: 12px;
}

.stTextInput input {
    background-color: #111827 !important;
    color: white !important;
    border: 1px solid #374151 !important;
}

.stButton button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# STOCK LIST (LEADERBOARD)
# ---------------------------------------------------
STOCKS = [
    "NVDA", "AAPL", "MSFT", "AMZN", "GOOGL",
    "META", "TSLA", "AMD", "NFLX", "PLTR"
]

# ---------------------------------------------------
# DATA FETCH
# ---------------------------------------------------
def get_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")
        info = stock.info
        return info, hist
    except:
        return None, None

# ---------------------------------------------------
# AI SUMMARY (8 SENTENCES)
# ---------------------------------------------------
def summary(ticker, score, hist):
    close = hist["Close"]

    change = ((close.iloc[-1] - close.iloc[0]) / close.iloc[0]) * 100
    volatility = close.pct_change().std() * 100

    trend = "upward" if close.iloc[-1] > close.mean() else "downward"

    return f"""
1. {ticker} has changed {change:.2f}% over the past six months.
2. The stock shows a {trend} trend in price movement.
3. Momentum is a key driver in the AI score.
4. Current volatility is {volatility:.2f}%.
5. Higher volatility reduces the AI score due to risk.
6. Moving average trends help determine strength.
7. The model combines growth, momentum, and risk.
8. Final classification: {rating(score)} (AI Score: {score}/100).
"""

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.markdown("# 📊 AI Stock Terminal")
st.markdown("### Institutional-style stock intelligence system")

# ---------------------------------------------------
# LEADERBOARD
# ---------------------------------------------------
st.markdown("## 🏆 AI Leaderboard")

rows = []

for t in STOCKS:
    info, hist = get_stock(t)
    if hist is None or hist.empty:
        continue

    score = calculate_ai_score(hist)

    rows.append({
        "Ticker": t,
        "AI Score": score,
        "Rating": rating(score)
    })

df = pd.DataFrame(rows)

if not df.empty:
    df = df.sort_values("AI Score", ascending=False)

    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.warning("No leaderboard data available.")

# ---------------------------------------------------
# SEARCH
# ---------------------------------------------------
st.markdown("---")
st.markdown("## 🔎 Analyze Stock")

ticker = st.text_input("Enter Stock Ticker", "AAPL").upper()

if ticker:
    info, hist = get_stock(ticker)

    if hist is None or hist.empty:
        st.error("No data found for this stock.")
    else:
        score = calculate_ai_score(hist)

        st.markdown(f"# {ticker}")
        st.markdown(f"### {rating(score)}")

        col1, col2, col3 = st.columns(3)

        col1.metric("AI Score", f"{score}/100")
        col2.metric("Price", f"${hist['Close'].iloc[-1]:.2f}")

        return_6m = ((hist["Close"].iloc[-1] - hist["Close"].iloc[0]) /
                     hist["Close"].iloc[0]) * 100

        col3.metric("6M Return", f"{return_6m:.2f}%")

        # Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": color(score)},
                "steps": [
                    {"range": [0, 35], "color": "#3f0d12"},
                    {"range": [35, 55], "color": "#5a2d0c"},
                    {"range": [55, 75], "color": "#4a4a08"},
                    {"range": [75, 100], "color": "#052e16"}
                ]
            }
        ))

        fig.update_layout(
            paper_bgcolor="#0b0f19",
            font={"color": "white"},
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)

        # Chart
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=hist.index,
            y=hist["Close"],
            mode="lines"
        ))

        fig2.update_layout(
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font={"color": "white"}
        )

        st.plotly_chart(fig2, use_container_width=True)

        # SUMMARY
        st.markdown("## 🧠 AI Summary")
        st.write(summary(ticker, score, hist))
