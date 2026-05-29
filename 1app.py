import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ai_score import calculate_ai_score, rating

# ---------------- UI ----------------
st.set_page_config(page_title="AI Stock Terminal", layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #0b0f19;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 AI Stock Terminal")

STOCKS = ["NVDA","AAPL","MSFT","GOOGL","AMZN","META","TSLA","AMD","NFLX","JPM"]

# ---------------- DATA ----------------
def get_stock(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo")
    return hist

# ---------------- LEADERBOARD ----------------
st.header("🏆 AI Leaderboard")

rows = []

for t in STOCKS:
    hist = get_stock(t)
    if hist.empty:
        continue

    score = calculate_ai_score(hist)

    rows.append({
        "Ticker": t,
        "AI Score": score,
        "Rating": rating(score)
    })

df = pd.DataFrame(rows).sort_values("AI Score", ascending=False)

st.dataframe(df, use_container_width=True, hide_index=True)

# ---------------- SEARCH ----------------
st.markdown("---")
st.header("🔎 Analyze Stock")

ticker = st.text_input("Enter ticker", "NVDA").upper()

if ticker:
    hist = get_stock(ticker)

    if hist.empty:
        st.error("No data found")
    else:
        score = calculate_ai_score(hist)

        st.subheader(ticker)
        st.markdown(f"### {rating(score)}")

        col1, col2, col3 = st.columns(3)

        col1.metric("AI Score", score)
        col2.metric("Price", f"${hist['Close'].iloc[-1]:.2f}")
        col3.metric("6M Return",
                    f"{((hist['Close'].iloc[-1]-hist['Close'].iloc[0])/hist['Close'].iloc[0])*100:.2f}%")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode="lines"))
        st.plotly_chart(fig, use_container_width=True)
