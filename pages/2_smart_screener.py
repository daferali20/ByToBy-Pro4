import streamlit as st
import pandas as pd

st.title("🔍 الفلتر الذكي للأسهم | Smart Screener")

with st.expander("⚙️ إعدادات وتصفية المؤشرات", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        market = st.selectbox("السوق", ["السوق السعودي (TASI)", "السوق الأمريكي (US)"])
        pe_range = st.slider("مكرر الربحية (P/E Ratio)", 0, 100, (5, 25))
    with col2:
        rsi_range = st.slider("مؤشر القوة النسبية (RSI)", 0, 100, (30, 70))
        min_volume = st.number_input("أدنى حجم تداول يومي", value=100000)
    with col3:
        pattern = st.multiselect("نماذج فنية مكتشفة", ["اختراق مقاوة", "قاع مزدوج", "RSI Inverted", "Bullish engulfing"])
        dividend_yield = st.slider("العائد على التوزيعات (%)", 0.0, 15.0, (2.0, 8.0))

# Mock Screened Data
screener_data = pd.DataFrame({
    "الرمز": ["2010.SR", "1150.SR", "MSFT", "AMD"],
    "الشركة": ["سابك", "الإنماء", "Microsoft", "AMD"],
    "السعر": [78.50, 32.10, 440.20, 160.50],
    "P/E": [14.2, 12.8, 32.1, 28.4],
    "RSI (14)": [42.1, 58.4, 62.0, 34.5],
    "توصية AI": ["شراء قوي", "احتفاظ", "شراء", "شراء قوي"]
})

st.subheader("📋 نتائج الفحص")
st.dataframe(screener_data, use_container_width=True)
