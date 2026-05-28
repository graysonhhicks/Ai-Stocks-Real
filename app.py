import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import warnings

warnings.filterwarnings("ignore")

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="AI Stock Terminal",
    page_icon="📈",
    layout="wide"
)

# ---------------------------------------------------
# DARK MODE UI (NIGHT TERMINAL)
# ---------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #05070d;
    color: white;
}

.block-container {
    padding: 2rem 2rem 3rem 2rem;
}

h1, h2, h3 {
    color: white;
}

.stTextInput input {
    background-color: #0f172a !important;
    color: white !important;
    border: 1px solid #334155 !important;
}

[data-testid="metric-container"] {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 16px;
}

.stDataFrame {
    background: #0f172a;
}

header, footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 AI Stock Terminal")
st.caption("Momentum + Risk + Trend Intelligence System")

# ---------------------------------------------------
# STOCK UNIVERSE
# ---------------------------------------------------
STOCKS = [
    "NVDA","AAPL","MSFT","GOOGL","AMZN",
    "META","TSLA","AMD","NFLX","PLTR",
    "JPM","V","MA","DIS","INTC"
]

# ---------------------------------------------------
# DATA FETCH
# ---------------------------------------------------
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")

        if hist is None or hist.empty:
            return None

        return hist

    except:
        return None

# ---------------------------------------------------
# AI SCORE ENGINE (STABLE VERSION)
# ---------------------------------------------------
def calculate_ai_score(hist):
    if hist is None or len(hist) < 60:
        return 0

    close = hist["Close"]

    try:
        return_6m = (close.iloc[-1] / close.iloc[0]) - 1
        momentum = (close.iloc[-1] / close.iloc[-20]) - 1

        volatility = close.pct_change().std()

        ma20 = close.tail(20).mean()
        ma50 = close.tail(50).mean()
        trend = 1 if ma20 > ma50 else -1

        score = (
            return_6m * 50 +
            momentum * 30 +
            trend * 10 -
            volatility * 20
        )

        score = max(0, min(100, score * 100))
        return round(score, 2)

    except:
        return 0

# ---------------------------------------------------
# RATING SYSTEM
# ---------------------------------------------------
def rating(score):
    if score >= 75:
        return "🟢 Lucarative BUY"
    elif score >= 55:
        return "🟡 Mid"
    elif score >= 35:
        return "🟠 Potential Finacail Loss"
    else:
        return "🔴 AVOID"

# ---------------------------------------------------
# COLOR TAG
# ---------------------------------------------------
def color_tag(score):
    if score >= 75:
        return "green"
    elif score >= 55:
        return "orange"
    else:
        return "red"

# ---------------------------------------------------
# LEADERBOARD
# ---------------------------------------------------
st.markdown("## 🏆 AI Leaderboard")

rows = []

for t in STOCKS:
    hist = get_stock_data(t)

    if hist is None:
        continue

    score = calculate_ai_score(hist)

    rows.append({
        "Ticker": t,
        "AI Score": score,
        "Rating": rating(score),
        "Signal": color_tag(score)
    })

df = pd.DataFrame(rows)

if not df.empty:
    df = df.sort_values("AI Score", ascending=False)

    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.warning("No data available")

# ---------------------------------------------------
# STOCK ANALYSIS
# ---------------------------------------------------
st.markdown("---")
st.markdown("## 🔎 Analyze Stock")

ticker = st.text_input("Enter Stock Ticker", "NVDA").upper()

if ticker:
    hist = get_stock_data(ticker)

    if hist is None:
        st.error("No data found")
    else:
        score = calculate_ai_score(hist)

        close = hist["Close"]
        return_6m = ((close.iloc[-1] / close.iloc[0]) - 1) * 100

        st.markdown(f"## {ticker}")
        st.markdown(f"### {rating(score)}")

        col1, col2, col3 = st.columns(3)

        col1.metric("AI Score", f"{score}/100")
        col2.metric("Price", f"${close.iloc[-1]:.2f}")
        col3.metric("6M Return", f"{return_6m:.2f}%")

        # PRICE CHART
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=close,
            mode="lines"
        ))

        fig.update_layout(
            paper_bgcolor="#05070d",
            plot_bgcolor="#05070d",
            font=dict(color="white"),
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)

        # SUMMARY (8 SENTENCES STYLE)
        st.markdown("## 🧠 AI Analysis")

        summary = f"""
1. {ticker} shows a 6-month return of {return_6m:.2f}%.
2. Momentum indicates current short-term trend strength.
3. Volatility levels influence overall risk scoring.
4. Moving average trend helps determine direction bias.
5. AI score combines return, momentum, and risk factors.
6. Higher scores indicate stronger institutional-grade signals.
7. Lower scores indicate higher downside risk exposure.
8. Final classification: {rating(score)} with score {score}/100.
"""

        st.write(summary)
