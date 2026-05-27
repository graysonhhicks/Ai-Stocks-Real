import streamlit as st
import requests
import yfinance as yf
import plotly.graph_objects as go

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="AI Stock Analyzer (FMP)", layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: black;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 AI Stock Analyzer (FMP Institutional Model)")

API_KEY = "YOUR_API_KEY_HERE"

# ----------------------------
# FMP DATA FETCH
# ----------------------------
def get_fmp_data(ticker):

    url = f"https://financialmodelingprep.com/api/v3/key-metrics/{ticker}?apikey={API_KEY}"
    r = requests.get(url).json()

    if not r:
        return None

    data = r[0]

    revenue_growth = data.get("revenueGrowth", 0) * 100
    roe = data.get("roe", 0) * 100
    pe = data.get("peRatio", 15)

    # Margins endpoint (extra call)
    url2 = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?limit=1&apikey={API_KEY}"
    r2 = requests.get(url2).json()

    if r2:
        gross_profit = r2[0].get("grossProfitRatio", 0) * 100
        operating_income = r2[0].get("operatingIncomeRatio", 0) * 100
    else:
        gross_profit = 0
        operating_income = 0

    # Score model (more realistic than before)
    score = (
        revenue_growth * 0.40 +
        gross_profit * 0.25 +
        operating_income * 0.15 +
        roe * 0.20
    )

    # Rating
    if score >= 68:
        rating = "Lucrative / Profitable"
    elif score >= 50:
        rating = "Neutral Profit"
    else:
        rating = "Unlikely Profitable"

    return {
        "revenue_growth": revenue_growth,
        "roe": roe,
        "gross_margin": gross_profit,
        "operating_margin": operating_income,
        "score": score,
        "rating": rating,
        "pe": pe
    }

# ----------------------------
# MAIN INPUT
# ----------------------------
ticker = st.text_input("Enter Stock Ticker", "AAPL")

if ticker:

    fmp = get_fmp_data(ticker)

    if not fmp:
        st.error("No data found. Check ticker or API key.")
        st.stop()

    # Yahoo price data (ONLY for chart)
    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo")

    st.subheader(f"{ticker} Analysis")

    col1, col2, col3 = st.columns(3)

    col1.metric("Revenue Growth", f"{fmp['revenue_growth']:.2f}%")
    col2.metric("Gross Margin", f"{fmp['gross_margin']:.2f}%")
    col3.metric("Operating Margin", f"{fmp['operating_margin']:.2f}%")

    st.write("ROE:", f"{fmp['roe']:.2f}%")
    st.write("P/E Ratio:", fmp["pe"])

    st.subheader(f"AI Score: {fmp['score']:.2f}")
    st.subheader(f"Prediction: {fmp['rating']}")

    # ----------------------------
    # CHART (YAHOO ONLY)
    # ----------------------------
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist["Close"],
        mode="lines",
        line=dict(color="white"),
        name="Price"
    ))

    fig.update_layout(
        title="6-Month Stock Price Chart",
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white")
    )

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------
    # AI SUMMARY
    # ----------------------------
    summary = f"""
    {ticker} shows revenue growth of {fmp['revenue_growth']:.2f}%, indicating expansion strength.
    The company has a gross margin of {fmp['gross_margin']:.2f}%, showing product-level profitability.
    Operating margin is {fmp['operating_margin']:.2f}%, reflecting efficiency after costs.
    Return on equity is {fmp['roe']:.2f}%, showing capital efficiency.
    The AI model produces a score of {fmp['score']:.2f}.
    Based on this, the stock is classified as {fmp['rating']}.
    Price movement is analyzed separately using Yahoo Finance data.
    Overall, this system uses institutional-style financial modeling similar to professional screening tools.
    """

    st.subheader("AI Analysis Summary")
    st.write(summary)
