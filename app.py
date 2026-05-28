import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import warnings

warnings.filterwarnings('ignore')

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="AI Stock Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------
# DARK MODE / PROFESSIONAL UI
# ---------------------------------------------------
st.markdown("""
<style>

/* Entire App */
.stApp {
    background-color: #0b0f19;
    color: white;
}

/* Main block */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Headers */
h1, h2, h3 {
    color: white;
    font-weight: 700;
}

/* Metric Cards */
[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1f2937;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0px 0px 15px rgba(0,0,0,0.35);
}

/* Dataframe */
[data-testid="stDataFrame"] {
    background-color: #111827;
    border-radius: 12px;
    border: 1px solid #1f2937;
}

/* Text Input */
.stTextInput input {
    background-color: #111827 !important;
    color: white !important;
    border: 1px solid #374151 !important;
    border-radius: 10px !important;
}

/* Buttons */
.stButton button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 18px;
    font-weight: 600;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
}

/* Table text */
table {
    color: white !important;
}

/* Remove toolbar */
header {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.markdown("""
# 📊 AI Stock Terminal

### Institutional-Style Stock Intelligence Dashboard
""")

# ---------------------------------------------------
# STOCK LIST
# ---------------------------------------------------
STOCKS = [
    "NVDA", "AAPL", "MSFT", "GOOGL", "AMZN",
    "META", "TSLA", "AMD", "NFLX", "PLTR",
    "JPM", "V", "MA", "DIS", "INTC"
]

# ---------------------------------------------------
# DATA FUNCTION - NO CACHING TO AVOID MANAGER ISSUES
# ---------------------------------------------------
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")

        if hist.empty:
            return None, None

        info = stock.info
        return info, hist

    except Exception as e:
        print(f"Error fetching {ticker}: {str(e)}")
        return None, None

# ---------------------------------------------------
# AI SCORE ENGINE
# ---------------------------------------------------
def calculate_ai_score(hist):
    if hist is None or hist.empty:
        return 0
    
    close = hist["Close"]
    
    if len(close) < 50:
        return 0

    try:
        # 6 month return
        return_6m = (
            (close.iloc[-1] - close.iloc[0])
            / close.iloc[0]
        )

        # recent momentum
        momentum = (
            (close.iloc[-1] - close.iloc[-20])
            / close.iloc[-20]
        )

        # volatility penalty
        volatility = close.pct_change().std()

        # moving average trend
        ma20 = close.tail(20).mean()
        ma50 = close.tail(50).mean()

        trend_bonus = 0.15 if ma20 > ma50 else -0.15

        # final score
        score = (
            (return_6m * 45) +
            (momentum * 35) -
            (volatility * 30) +
            (trend_bonus * 100)
        )

        score = max(0, min(100, score * 100))
        return round(score, 2)
    
    except Exception as e:
        print(f"Score calculation error: {e}")
        return 0

# ---------------------------------------------------
# RATING SYSTEM
# ---------------------------------------------------
def rating(score):
    if score >= 75:
        return "🟢 ELITE"
    elif score >= 55:
        return "🟡 SOLID"
    elif score >= 35:
        return "🟠 RISKY"
    else:
        return "🔴 WEAK"

# ---------------------------------------------------
# COLOR FOR GAUGE
# ---------------------------------------------------
def gauge_color(score):
    if score >= 75:
        return "#22c55e"
    elif score >= 55:
        return "#eab308"
    elif score >= 35:
        return "#f97316"
    else:
        return "#ef4444"

# ---------------------------------------------------
# SUMMARY GENERATOR
# ---------------------------------------------------
def generate_summary(ticker, score, hist):
    close = hist["Close"]

    change = (
        (close.iloc[-1] - close.iloc[0])
        / close.iloc[0]
    ) * 100

    volatility = (
        close.pct_change().std()
    ) * 100

    trend = (
        "upward"
        if close.iloc[-1] > close.mean()
        else "downward"
    )

    return f"""
1. {ticker} has moved {change:.2f}% over the past six months.

2. The stock currently shows a primarily {trend} trading trend.

3. Momentum indicators are included in the AI scoring system.

4. Volatility currently sits around {volatility:.2f}%.

5. Stronger momentum and lower volatility improve ratings.

6. The AI engine combines return strength, trend analysis, and risk metrics.

7. Institutional-style weighting is used to evaluate the stock.

8. Overall classification: {rating(score)} with an AI Score of {score}/100.
"""

# ---------------------------------------------------
# LEADERBOARD
# ---------------------------------------------------
st.markdown("## 🏆 AI Leaderboard")

with st.spinner("Loading leaderboard..."):
    leaderboard_rows = []

    for ticker in STOCKS:
        info, hist = get_stock_data(ticker)

        if hist is None:
            continue

        score = calculate_ai_score(hist)

        leaderboard_rows.append({
            "Ticker": ticker,
            "AI Score": round(score, 2),
            "Rating": rating(score)
        })

if leaderboard_rows:
    leaderboard = pd.DataFrame(leaderboard_rows)
    leaderboard = leaderboard.sort_values(
        by="AI Score",
        ascending=False
    )

    st.dataframe(
        leaderboard,
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("Unable to load leaderboard data. Please try again.")

# ---------------------------------------------------
# STOCK SEARCH
# ---------------------------------------------------
st.markdown("---")
st.markdown("## 🔎 Analyze Individual Stock")

ticker = st.text_input(
    "Enter Stock Ticker",
    "NVDA"
).upper()

# ---------------------------------------------------
# STOCK ANALYSIS
# ---------------------------------------------------
if ticker:
    info, hist = get_stock_data(ticker)

    if hist is None:
        st.error("Stock data unavailable.")
    else:
        score = calculate_ai_score(hist)
        company_name = info.get("longName", ticker) if info else ticker
        current_price = hist["Close"].iloc[-1]

        # HEADER
        st.markdown(f"# {company_name}")
        st.markdown(f"### {rating(score)}")

        # METRICS
        col1, col2, col3 = st.columns(3)

        col1.metric("AI Score", f"{score}/100")
        col2.metric("Current Price", f"${current_price:.2f}")

        six_month_return = (
            (
                hist["Close"].iloc[-1]
                - hist["Close"].iloc[0]
            )
            / hist["Close"].iloc[0]
        ) * 100

        col3.metric("6M Return", f"{six_month_return:.2f}%")

        # AI GAUGE
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            number={
                "font": {
                    "color": "white",
                    "size": 42
                }
            },
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickcolor": "white"
                },
                "bar": {
                    "color": gauge_color(score)
                },
                "bgcolor": "#111827",
                "borderwidth": 2,
                "bordercolor": "#374151",
                "steps": [
                    {"range": [0, 35], "color": "#3f0d12"},
                    {"range": [35, 55], "color": "#5a2d0c"},
                    {"range": [55, 75], "color": "#4a4a08"},
                    {"range": [75, 100], "color": "#052e16"}
                ]
            }
        ))

        fig_gauge.update_layout(
            paper_bgcolor="#0b0f19",
            font={"color": "white"},
            height=350
        )

        st.plotly_chart(fig_gauge, use_container_width=True)

        # PRICE CHART
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist["Close"],
            mode="lines",
            name="Close Price",
            line=dict(
                color="#22c55e",
                width=3
            )
        ))

        fig.update_layout(
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font=dict(color="white"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            height=500,
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

        # SUMMARY
        st.markdown("## 🧠 AI Analysis")
        st.write(generate_summary(ticker, score, hist))
