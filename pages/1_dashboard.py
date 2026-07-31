import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf

st.title("📊 لوحة التحكم القيادية | Dashboard")

st.subheader("📌 نظرة عامة على المؤشرات الرئيسية")
m1, m2, m3, m4 = st.columns(4)
m1.metric("مؤشر تداول (TASI)", "11,850.40", "+45.20 (+0.38%)")
m2.metric("مؤشر S&P 500", "5,450.10", "-12.30 (-0.23%)")
m3.metric("سعر النفط (برنت)", "$82.40", "+1.15 (+1.41%)")
m4.metric("الذهب", "$2,380.00", "+5.20 (+0.22%)")

st.divider()

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 أداء المؤشر العام")
    df = yf.download("^TASI.SR" if yf.Ticker("^TASI.SR").history().shape[0] > 0 else "AAPL", period="1mo", interval="1d")
    if not df.empty:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", height=380, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🔥 الأكثر حركة اليوم")
    top_movers = pd.DataFrame({
        "الرمز": ["2222.SR", "1120.SR", "NVDA", "AAPL"],
        "الشركة": ["أرامكو", "الراجحي", "Nvidia", "Apple"],
        "التغير": ["+1.2%", "+2.4%", "-0.8%", "+1.5%"],
        "الحجم": ["12.5M", "8.2M", "45.1M", "30.0M"]
    })
    st.dataframe(top_movers, hide_index=True, use_container_width=True)
