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

st.title("📊 AI Stock Analyzer (FMP + Yahoo Finance)")

# ----------------------------
# API KEY (SAFE FALLBACK)
# ----------------------------
API_KEY = st.secrets.get("FMP_API_KEY", None)

if not API_KEY:
    st.warning("⚠️ FMP API key missing. Add it in Streamlit Secrets as FMP_API_KEY.")
    st.stop()

# ----------------------------
# SAFE FMP FETCH
# ----------------------------
def get_fmp_data(ticker):

    try:
        url = f"https://financialmodelingprep.com/api/v3/key-metrics/{ticker}?apikey={API_KEY}"
        r = requests.get(url, timeout=10).json()

        if not isinstance(r, list) or len(r) == 0:
            return None

        data = r[0]

        revenue_growth = data.get("revenueGrowth", 0) * 100
        roe = data.get("roe", 0) * 100
        pe = data.get("peRatio", 15)

        url2 = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?limit=1&apikey={API_KEY}"
        r2 = requests.get(url2, timeout=10).json()

        gross_margin = 0
        operating_margin = 0

        if isinstance(r2, list) and len(r2) > 0:
            gross_margin = r2[0].get("grossProfitRatio", 0) * 100
            operating_margin = r2[0].get("operatingIncomeRatio", 0) * 100

        score = (
            revenue_growth * 0.40 +
            gross_margin * 0.25 +
            operating_margin * 0.15 +
            roe * 0.20
        )

        if score >= 55:
            rating = "Lucrative / Profitable"
        elif score >= 30:
            rating = "Neutral Profit"
        else:
            rating = "Unlikely Profitable"

        return {
            "revenue_growth": revenue_growth,
            "roe": roe,
            "gross_margin": gross_margin,
            "operating_margin": operating_margin,
            "score": score,
            "rating": rating,
            "pe": pe
        }

    except Exception as e:
        return None

# ----------------------------
# USER INPUT
# ----------------------------
ticker = st.text_input("Enter Stock Ticker", "AAPL")

if ticker:

    fmp = get_fmp_data(ticker)

    if not fmp:
        st.error("No data found for this ticker (or API limit reached).")
        st.stop()

    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo")

    # ----------------------------
    # METRICS
    # ----------------------------
    st.subheader(f"Analysis: {ticker}")

    col1, col2, col3 = st.columns(3)

    col1.metric("Revenue Growth", f"{fmp['revenue_growth']:.2f}%")
    col2.metric("Gross Margin", f"{fmp['gross_margin']:.2f}%")
    col3.metric("Operating Margin", f"{fmp['operating_margin']:.2f}%")

    st.write(f"**ROE:** {fmp['roe']:.2f}%")
    st.write(f"**P/E Ratio:** {fmp['pe']}")

    st.subheader(f"AI Score: {fmp['score']:.2f}")
    st.subheader(f"Prediction: {fmp['rating']}")

    # ----------------------------
    # PRICE CHART
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
        title="6-Month Price Chart",
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white")
    )

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------
    # SUMMARY (8 SENTENCES)
    # ----------------------------
    summary = f"""
    {ticker} is being analyzed using a weighted financial model combining growth, margins, and return on equity. 
    The company shows a revenue growth rate of {fmp['revenue_growth']:.2f}%, which reflects its expansion strength. 
    Its gross margin is {fmp['gross_margin']:.2f}%, indicating profitability at the product level. 
    Operating margin stands at {fmp['operating_margin']:.2f}%, showing efficiency after operating costs. 
    Return on equity is {fmp['roe']:.2f}%, measuring how effectively the company uses shareholder capital. 
    The overall AI score is {fmp['score']:.2f}, based on a weighted institutional-style model. 
    Based on this analysis, the stock is classified as {fmp['rating']}. 
    Price trends are shown separately using Yahoo Finance for visual confirmation of performance.
    """

    st.subheader("AI Summary")
    st.write(summary)
