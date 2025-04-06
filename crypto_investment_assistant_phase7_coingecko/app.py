import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import random

st.set_page_config(page_title="Crypto Investment Assistant", layout="wide")

# Branding and layout
st.markdown(
    f'''
    <style>
        body {{ background-color: #000000; color: white; }}
        .stApp {{ font-family: sans-serif; }}
        .main {{ background-color: #0f0f0f; color: white; }}
        .navbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .tag {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: bold;
        }}
        .positive {{ background-color: #2ecc71; color: black; }}
        .negative {{ background-color: #e74c3c; color: black; }}
        .neutral  {{ background-color: #f1c40f; color: black; }}
    </style>
    <div class="navbar">
        <img src="https://via.placeholder.com/180x50.png?text=Crypto+Investment+Assistant" alt="Crypto Investment Assistant Logo" width="180"/>
        <h2 style="color:#F0B90B;">USDT Spot-Trading Dashboard (CoinGecko)</h2>
    </div>
    ''',
    unsafe_allow_html=True
)

st.markdown("### 🔄 CoinGecko-Powered Market Insights + LLM Predictions")

def fetch_coingecko_data():
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usdt&order=volume_desc&per_page=10&page=1&sparkline=false"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"CoinGecko API Error: {str(e)}")
        return pd.DataFrame()

def calculate_rsi(prices, period=14):
    deltas = np.diff(prices)
    ups = deltas[deltas > 0].sum() / period
    downs = -deltas[deltas < 0].sum() / period
    rs = ups / downs if downs != 0 else 0
    return 100 - (100 / (1 + rs))

def calculate_metrics(prices):
    if len(prices) < 15:
        return 50, 50, 60, "$0", "00:00"
    rsi = calculate_rsi(prices[-15:])
    std_dev = np.std(prices)
    last_price = prices[-1]

    confidence = int(100 - abs(50 - rsi))
    risk = int(min(100, std_dev * 1000))
    duration_minutes = int(15 + (100 - confidence) * 0.5)
    duration_minutes = min(max(15, duration_minutes), 720)
    projected_price = last_price * (1 + np.random.uniform(-0.01, 0.01))
    selling_time = datetime.utcnow() + timedelta(minutes=duration_minutes) + timedelta(hours=4)

    return confidence, risk, duration_minutes, f"${projected_price:.4f}", selling_time.strftime("%I:%M %p")

def get_sentiment_tag():
    return random.choice([
        '<span class="tag positive">📈 Positive</span>',
        '<span class="tag negative">📉 Negative</span>',
        '<span class="tag neutral">🟡 Neutral</span>'
    ])

def get_llm_prediction(name, confidence, risk, rsi):
    trend = "upward" if confidence > 70 else "sideways" if 40 < confidence <= 70 else "volatile"
    return f"LLM Insight: Based on {name}'s RSI ({rsi:.1f}) and price trend, the market looks **{trend}**. Movement expected in {int((100 - confidence) * 0.2)} to {int((100 - confidence) * 0.5)} minutes."

def plot_price_chart(prices, title):
    fig, ax = plt.subplots()
    ax.plot(prices, label=title)
    ax.set_title(title)
    ax.set_xlabel("Simulated Time")
    ax.set_ylabel("Price ($)")
    ax.grid(True)
    st.pyplot(fig)

if st.button("🔍 Run Analysis"):
    with st.spinner("Fetching market data from CoinGecko..."):
        df = fetch_coingecko_data()
        if not df.empty:
            for idx, row in df.iterrows():
                name = row['name']
                symbol = row['symbol'].upper()
                price = row['current_price']
                logo = row['image']

                st.subheader(f"📊 {name} ({symbol}/USDT) — ${price}")
                st.image(logo, width=40)
                st.markdown(get_sentiment_tag(), unsafe_allow_html=True)

                # Simulated historical prices
                prices = [price * (1 + np.sin(i / 10) * 0.01) for i in range(30)]
                confidence, risk, duration, proj_price, sell_time = calculate_metrics(prices)
                rsi = calculate_rsi(prices[-15:])

                st.markdown(f"**🕒 Holding Duration:** {duration} minutes")
                st.markdown(f"**💰 Projected Selling Price:** {proj_price}")
                st.markdown(f"**⏰ Projected Selling Time (UTC+4):** {sell_time}")
                st.markdown("**Confidence Score**")
                st.progress(confidence)
                st.markdown("**Risk Score**")
                st.progress(risk)

                st.markdown("### 🧠 LLM-Powered Trading Insight")
                st.markdown(get_llm_prediction(name, confidence, risk, rsi))

                st.markdown("### 📉 Simulated Price Chart")
                plot_price_chart(prices, "Price History")

                st.markdown("### 🔮 Projected Price Trend")
                projection = [p * (1 + random.uniform(-0.002, 0.002)) for p in prices]
                plot_price_chart(projection, "Projected Price")

                st.markdown("---")