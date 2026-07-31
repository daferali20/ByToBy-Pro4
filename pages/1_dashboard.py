# pages/1_dashboard.py

import streamlit as st
import sys, os
import plotly.graph_objects as go
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.config import US_MARKET_INDEXES, US_STOCK_WATCHLIST
from backend.data_providers.market_data import USMarketDataProvider

st.title("🇺🇸 US Stock Market Dashboard | لوحة الأسهم الأمريكية")

# 1. عرض المؤشرات الأمريكية المباشرة
st.subheader("📌 Real-Time Market Indexes | المؤشرات الرئيسية")

idx_cols = st.columns(len(US_MARKET_INDEXES))
for i, (name, symbol) in enumerate(US_MARKET_INDEXES.items()):
    provider = USMarketDataProvider(symbol)
    price_info = provider.get_realtime_price()
    
    if "error" not in price_info:
        delta_val = f"{price_info['change']} ({price_info['change_pct']}%)"
        idx_cols[i].metric(
            label=name,
            value=f"${price_info['current_price']:,}",
            delta=delta_val
        )

st.divider()

# 2. الرسم البياني للأسهم وتفاصيل الأداء
col_left, col_right = st.columns([2, 1])

with col_left:
    selected_stock = st.selectbox("Select US Stock | اختر سهماً للعرض:", US_STOCK_WATCHLIST, index=0)
    
    provider = USMarketDataProvider(selected_stock)
    df = provider.get_history(period="6mo")
    
    if not df.empty:
        st.subheader(f"📈 Chart: {selected_stock} (6 Months)")
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name=selected_stock
        )])
        fig.update_layout(template="plotly_dark", height=420, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🔥 Top Watchlist Quotes")
    
    table_data = []
    for sym in US_STOCK_WATCHLIST[:6]: # جلب أفضل 6 أسهم بشكل سريع
        p = USMarketDataProvider(sym).get_realtime_price()
        if "error" not in p:
            table_data.append({
                "Symbol": p["symbol"],
                "Price ($)": f"${p['current_price']}",
                "Change (%)": f"{p['change_pct']}%"
            })
    
    st.dataframe(pd.DataFrame(table_data), hide_index=True, use_container_width=True)
