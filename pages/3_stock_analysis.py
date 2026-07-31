# pages/3_stock_analysis.py

import streamlit as st
#import sys, os
import plotly.graph_objects as go
import sys
import os

# إضافة مجلد الجذر الرئيسي للمشروع إلى مسار بايثون
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import plotly.graph_objects as go

# الآن يتم الاستدعاء بدون أي أخطاء
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

        st.subheader(f"🏢 {fund['company_name']} ({report['symbol']})")
        st.caption(f"**Sector:** {fund['sector']} | **Industry:** {fund['industry']}")

        # مقاييس حقيقية مباشرة
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Current Price", f"${live['current_price']}", f"{live['change_pct']}%")
        m2.metric("P/E Ratio", f"{fund['pe_ratio']:.2f}" if fund['pe_ratio'] else "N/A")
        m3.metric("52-Week High", f"${fund['52_week_high']}")
        m4.metric("52-Week Low", f"${fund['52_week_low']}")

        st.divider()

        # تشغيل التنبؤ بالذكاء الاصطناعي
        st.subheader("🤖 AI Real-Time Valuation & Forecast")
        
        predictor = StockPricePredictor(df)
        pred_res = predictor.train_and_predict_next_day()

        if "error" not in pred_res:
            c1, c2, c3 = st.columns(3)
            c1.metric("Predicted Next Day Price", f"${pred_res['predicted_price']}", f"{pred_res['expected_change_pct']}%")
            c2.metric("RSI (14)", f"{tech['rsi_value']}", tech['rsi_status'])
            c3.metric("Trend", tech['trend'])

        # التوصية الاستثمارية المباشرة
        rec = RecommendationEngine.get_final_recommendation(
            symbol=report['symbol'],
            current_price=live['current_price'],
            rsi=tech['rsi_value'],
            pe=fund['pe_ratio'] if fund['pe_ratio'] else 20.0,
            margin=0.18,
            eps=fund['eps'] if fund['eps'] else 1.0,
            growth=0.08,
            trend=tech['trend']
        )

        st.info(f"**AI Recommendation:** {rec['action_summary']}")

        # رسم الشموع اليابانية مع المتوسطات
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
        if 'SMA_20' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], mode='lines', name='SMA 20', line=dict(color='yellow')))
        if 'SMA_50' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], mode='lines', name='SMA 50', line=dict(color='cyan')))

        fig.update_layout(template="plotly_dark", height=480)
        st.plotly_chart(fig, use_container_width=True)
