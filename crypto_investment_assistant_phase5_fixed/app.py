import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

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
    </style>
    <div class="navbar">
        <img src="https://via.placeholder.com/180x50.png?text=Crypto+Investment+Assistant" alt="Crypto Investment Assistant Logo" width="180"/>
        <h2 style="color:#F0B90B;">Binance USDT Spot-Trading Dashboard</h2>
    </div>
    ''',
    unsafe_allow_html=True
)

st.markdown("### 🔄 Technical Analysis Based Suggestions")

def fetch_binance_data():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    res = requests.get(url)
    if res.status_code != 200:
        st.error("Failed to fetch data from Binance")
        return pd.DataFrame()
    data = res.json()
    usdt_pairs = [item for item in data if item['symbol'].endswith('USDT')]
    pairs_df = pd.DataFrame(usdt_pairs)
    pairs_df = pairs_df[['symbol', 'lastPrice', 'priceChangePercent', 'volume']]
    pairs_df.columns = ['Pair', 'Last Price ($)', '24h Change (%)', '24h Volume']
    pairs_df['Last Price ($)'] = pairs_df['Last Price ($)'].astype(float).round(4)
    pairs_df['24h Change (%)'] = pairs_df['24h Change (%)'].astype(float).round(2)
    pairs_df['24h Volume'] = pairs_df['24h Volume'].astype(float).round(2)
    return pairs_df

def fetch_candlestick_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=100"
    res = requests.get(url)
    if res.status_code != 200:
        return []
    return res.json()

def calculate_rsi(prices, period=14):
    deltas = np.diff(prices)
    ups = deltas[deltas > 0].sum() / period
    downs = -deltas[deltas < 0].sum() / period
    rs = ups / downs if downs != 0 else 0
    return 100 - (100 / (1 + rs))

def calculate_ema(prices, period=10):
    return pd.Series(prices).ewm(span=period, adjust=False).mean().iloc[-1]

def calculate_metrics(prices, volume):
    if len(prices) < 15:
        return 50, 50, 60, "$0", "00:00"
    rsi = calculate_rsi(prices[-15:])
    ema = calculate_ema(prices)
    std_dev = np.std(prices)
    last_price = prices[-1]

    confidence = int(100 - abs(50 - rsi))
    risk = int(min(100, std_dev * 1000))

    duration_minutes = int(15 + (100 - confidence) * 0.5)
    duration_minutes = min(max(15, duration_minutes), 720)
    projected_price = last_price * (1 + np.random.uniform(-0.01, 0.01))
    selling_time = datetime.utcnow() + timedelta(minutes=duration_minutes) + timedelta(hours=4)

    return confidence, risk, duration_minutes, f"${projected_price:.4f}", selling_time.strftime("%I:%M %p")

def plot_price_chart(prices, title):
    fig, ax = plt.subplots()
    ax.plot(prices, label=title)
    ax.set_title(title)
    ax.set_xlabel("Minutes Ago")
    ax.set_ylabel("Price ($)")
    ax.grid(True)
    st.pyplot(fig)

def get_token_icon(symbol):
    base = symbol.replace("USDT", "").lower()
    return f"https://cryptoicon-api.pages.dev/api/icon/{base}"

if st.button("🔍 Run Analysis"):
    with st.spinner("Performing technical analysis..."):
        df = fetch_binance_data()
        if not df.empty:
            for idx, row in df.iterrows():
                if idx >= 3:
                    break
                pair = row['Pair']
                last_price = row['Last Price ($)']
                token_icon_url = get_token_icon(pair)

                st.subheader(f"📊 {pair} — ${last_price}")
                st.image(token_icon_url, width=40)

                klines = fetch_candlestick_data(pair)
                if not klines:
                    st.warning("Failed to fetch candle data.")
                    continue

                close_prices = [float(k[4]) for k in klines]
                volumes = [float(k[5]) for k in klines]

                confidence, risk, duration, proj_price, sell_time = calculate_metrics(close_prices, volumes)

                st.markdown(f"**🕒 Holding Duration:** {duration} minutes")
                st.markdown(f"**💰 Projected Selling Price:** {proj_price}")
                st.markdown(f"**⏰ Projected Selling Time (UTC+4):** {sell_time}")
                st.markdown("**Confidence Score**")
                st.progress(confidence)
                st.markdown("**Risk Score**")
                st.progress(risk)

                st.markdown("### 📉 Real-Time Price Chart")
                plot_price_chart(close_prices[-30:], "Real-Time Price")

                st.markdown("### 🔮 Projected Price Trend (Simulated)")
                fake_projection = [p * (1 + np.random.uniform(-0.002, 0.002)) for p in close_prices[-30:]]
                plot_price_chart(fake_projection, "Projected Price")

                st.markdown("---")