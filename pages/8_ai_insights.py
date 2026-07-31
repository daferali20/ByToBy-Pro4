# pages/8_ai_insights.py

import os
import sys

# 1. ضمان التعرف على مجلد Root للمشروع على Streamlit Cloud
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st

# 2. الاستدعاء المباشر للكلاس الصحيح USMarketDataProvider
from backend.data_providers.market_data import USMarketDataProvider
from backend.analysis.technical import TechnicalAnalyzer

# تطبق الـ CSS المخصص إذا كان متوفراً
css_path = os.path.join(ROOT_DIR, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🤖 AI Market Insights & Deep Analytics")

symbol = st.text_input("Enter US Stock Ticker Symbol:", value="NVDA").upper()

if symbol:
    with st.spinner(f"Analyzing market patterns for {symbol}..."):
        provider = USMarketDataProvider(symbol)
        df = provider.get_history(period="6mo")

        if df.empty:
            st.error(f"Unable to fetch history data for {symbol}.")
        else:
            analyzer = TechnicalAnalyzer(df)
            analysis = analyzer.analyze_trend()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Technical Trend", analysis.get("trend", "N/A"))
            with col2:
                st.metric("RSI Level", f"{analysis.get('rsi_value', 0):.1f}")

            st.info(f"**MACD Signal Status:** {analysis.get('macd_signal', 'N/A')}")
