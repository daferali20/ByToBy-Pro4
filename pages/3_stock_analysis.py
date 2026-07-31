# pages/3_stock_analysis.py

import os
import sys

# 1. إضافة مجلد الجذر للمشروع في أول سطر لضمان معرفة السيرفر بمجلدات backend و ml_models
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import plotly.graph_objects as go
import streamlit as st

# 2. الاستدعاء بعد ضبط المسار بشكل صحيح
from backend.services.stock_service import USStockService
from ml_models.predictor import StockPricePredictor
from ml_models.recommendation import RecommendationEngine

st.title("🔬 US Stock Deep Analysis & AI Prediction")

symbol_input = st.text_input("Enter US Ticker Symbol (e.g., AAPL, NVDA, TSLA, MSFT):", value="AAPL")

if symbol_input:
    with st.spinner(f"Fetching real-time data for {symbol_input.upper()}..."):
        report = USStockService.get_full_stock_report(symbol_input)

    if "error" in report:
        st.error(report["error"])
    else:
        live = report["live"]
        fund = report["fundamentals"]
        tech = report["technical"]
        df = report["df"]

        st.subheader(f"🏢 {fund.get('company_name', report['symbol'])} ({report['symbol']})")
        st.caption(f"**Sector:** {fund.get('sector', 'N/A')} | **Industry:** {fund.get('industry', 'N/A')}")

        # مقاييس حقيقية مباشرة مع التحقق من وجود القيم
        m1, m2, m3, m4 = st.columns(4)
        
        change_pct_val = live.get('change_pct', 0.0)
        m1.metric("Current Price", f"${live.get('current_price', 0.0):,.2f}", f"{change_pct_val}%")
        
        pe_ratio = fund.get('pe_ratio')
        m2.metric("P/E Ratio", f"{pe_ratio:.2f}" if pe_ratio else "N/A")
        
        m3.metric("52-Week High", f"${fund.get('52_week_high', 0.0):,.2f}")
        m4.metric("52-Week Low", f"${fund.get('52_week_low', 0.0):,.2f}")

        st.divider()

        # تشغيل التنبؤ بالذكاء الاصطناعي
        st.subheader("🤖 AI Real-Time Valuation & Forecast")
        
        predictor = StockPricePredictor(df)
        pred_res = predictor.train_and_predict_next_day()

        if "error" not in pred_res:
            c1, c2, c3 = st.columns(3)
            c1.metric("Predicted Next Day Price", f"${pred_res['predicted_price']}", f"{pred_res['expected_change_pct']}%")
            c2.metric("RSI (14)", f"{tech.get('rsi_value', 'N/A')}", tech.get('rsi_status', 'N/A'))
            c3.metric("Trend", tech.get('trend', 'N/A'))

        # التوصية الاستثمارية المباشرة
        rec = RecommendationEngine.get_final_recommendation(
            symbol=report['symbol'],
            current_price=live.get('current_price', 0.0),
            rsi=tech.get('rsi_value', 50.0),
            pe=fund.get('pe_ratio') if fund.get('pe_ratio') else 20.0,
            margin=0.18,
            eps=fund.get('eps') if fund.get('eps') else 1.0,
            growth=0.08,
            trend=tech.get('trend', 'محايد')
        )

        st.info(f"**AI Recommendation:** {rec['action_summary']}")

        # رسم الشموع اليابانية مع المتوسطات
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Price"
        ))
        
        if 'SMA_20' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], mode='lines', name='SMA 20', line=dict(color='yellow')))
        if 'SMA_50' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], mode='lines', name='SMA 50', line=dict(color='cyan')))

        fig.update_layout(template="plotly_dark", height=480, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
