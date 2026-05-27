import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="AI Stock Analyzer",
    layout="wide"
)

st.title("AI-Powered Stock Market Analyzer")

# ----------------------------
# Safer Data Fetching (cached)
# ----------------------------
@st.cache_data
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)

    # safer alternatives to .info (which often breaks in cloud)
    try:
        info = stock.get_info() if hasattr(stock, "get_info") else {}
    except:
        info = {}

    hist = stock.history(period="6mo")

    return info, hist

# ----------------------------
# User Input
# ----------------------------
ticker = st.text_input("Enter Stock Ticker", "AAPL")

if ticker:

    info, hist = get_stock_data(ticker)

    # ----------------------------
    # Safe Financial Metrics
    # ----------------------------
    revenue_growth = (info.get("revenueGrowth") or 0) * 100
    profit_margin = (info.get("profitMargins") or 0) * 100
    roe = (info.get("returnOnEquity") or 0) * 100
    beta = info.get("beta") or 1

    # ----------------------------
    # AI Score
    # ----------------------------
    score = (
        revenue_growth * 0.50 +
        profit_margin * 0.30 +
        roe * 0.20
    )

    # ----------------------------
    # Rating System
    # ----------------------------
    if score >= 70:
        rating = "Lucrative / Profitable"
    elif score >= 40:
        rating = "Neutral Profit"
    else:
        rating = "Unlikely Profitable"

    # ----------------------------
    # Risk System
    # ----------------------------
    if beta > 1.5:
        risk = "High Risk"
    elif beta > 1:
        risk = "Medium Risk"
    else:
        risk = "Low Risk"

    # ----------------------------
    # Company Name
    # ----------------------------
    st.header(info.get("longName", ticker))

    # ----------------------------
    # Metrics UI
    # ----------------------------
    col1, col2, col3 = st.columns(3)

    col1.metric("Revenue Growth", f"{revenue_growth:.2f}%")
    col2.metric("Profit Margin", f"{profit_margin:.2f}%")
    col3.metric("Return on Equity", f"{roe:.2f}%")

    # ----------------------------
    # AI Output
    # ----------------------------
    st.subheader(f"AI Financial Score: {score:.2f}")
    st.subheader(f"Prediction: {rating}")
    st.subheader(f"Risk Level: {risk}")

    # ----------------------------
    # Stock Chart (safe check)
    # ----------------------------
    if hist is not None and not hist.empty:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=hist.index,
                y=hist["Close"],
                mode="lines",
                name="Stock Price"
            )
        )

        fig.update_layout(
            title="6-Month Stock Price History",
            xaxis_title="Date",
            yaxis_title="Price",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("No chart data available for this ticker.")

    # ----------------------------
    # AI Summary
    # ----------------------------
    summary = f"""
    {info.get('shortName', ticker)} analysis:

    Revenue growth is {revenue_growth:.2f}%, profit margins are {profit_margin:.2f}%, 
    and return on equity is {roe:.2f}%.

    The AI score is {score:.2f}, classifying this stock as {rating}.

    Risk level based on beta is {risk}.
    """

    st.subheader("AI Financial Summary")
    st.write(summary)
