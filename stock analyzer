import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# Website Configuration
st.set_page_config(
    page_title="AI Stock Analyzer",
    layout="wide"
)

# Website Title
st.title("AI-Powered Stock Market Analyzer")

# User Input
ticker = st.text_input("Enter Stock Ticker", "AAPL")

if ticker:

    # Pull Yahoo Finance Data
    stock = yf.Ticker(ticker)
    info = stock.info

    # Financial Metrics
    revenue_growth = info.get("revenueGrowth", 0) * 100
    profit_margin = info.get("profitMargins", 0) * 100
    roe = info.get("returnOnEquity", 0) * 100
    beta = info.get("beta", 1)

    # AI Weighted Formula
    score = (
        revenue_growth * 0.50
        + profit_margin * 0.30
        + roe * 0.20
    )

    # Profitability Ratings
    if score >= 70:
        rating = "Lucrative / Profitable"
    elif score >= 40:
        rating = "Neutral Profit"
    else:
        rating = "Unlikely Profitable"

    # Risk Analysis
    if beta > 1.5:
        risk = "High Risk"
    elif beta > 1:
        risk = "Medium Risk"
    else:
        risk = "Low Risk"

    # Company Information
    st.header(info.get("longName", ticker))

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "6-Month Revenue Growth",
        f"{revenue_growth:.2f}%"
    )

    col2.metric(
        "Profit Margin",
        f"{profit_margin:.2f}%"
    )

    col3.metric(
        "Return on Equity",
        f"{roe:.2f}%"
    )

    # AI Score Display
    st.subheader(f"AI Financial Score: {score:.2f}")
    st.subheader(f"Prediction: {rating}")
    st.subheader(f"Risk Level: {risk}")

    # 6-Month Stock Chart
    hist = stock.history(period="6mo")

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

    # AI Summary
    summary = f"""
    {info.get('shortName', ticker)} has demonstrated recent revenue growth of {revenue_growth:.2f}% based on Yahoo Finance financial reporting data.
    Current profit margins are approximately {profit_margin:.2f}%, indicating the company’s operational profitability.
    The company currently maintains a return on equity of {roe:.2f}%, which reflects how efficiently management uses shareholder capital.
    Using the weighted financial scoring system, the company received an AI financial score of {score:.2f}.
    Market volatility metrics currently classify this stock as {risk}.
    Revenue growth remains the most heavily weighted component of the system because expansion is often associated with future performance potential.
    Profitability and shareholder efficiency metrics also contribute significantly to the overall evaluation.
    Overall, the system categorizes this stock as {rating}.
    """

    st.subheader("AI Financial Summary")
    st.write(summary)
