# pages/3_stock_analysis.py

import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from backend.services.stock_service import USStockService
from backend.analysis.charts import build_advanced_stock_chart
from backend.services.notifier import AlertNotifier
from ml_models.predictor import StockPricePredictor
from ml_models.recommendation import RecommendationEngine

# تطبيق CSS المخصص
css_path = os.path.join(ROOT_DIR, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("⚡ ByToBy-Pro4 | US Stock Terminal")

# شريط إدخال وإعدادات التنبيه
col_sym, col_tele_token, col_chat = st.columns([2, 2, 2])
with col_sym:
    symbol_input = st.text_input("US Ticker:", value="NVDA").upper()
with col_tele_token:
    tg_token = st.text_input("Telegram Bot Token (اختياري):", type="password")
with col_chat:
    tg_chat_id = st.text_input("Telegram Chat ID (اختياري):", type="password")

if symbol_input:
    with st.spinner(f"Loading live data for {symbol_input}..."):
        report = USStockService.get_full_stock_report(symbol_input)

    if "error" in report:
        st.error(report["error"])
    else:
        live = report["live"]
        fund = report["fundamentals"]
        tech = report["technical"]
        df = report["df"]

        # بطاقات المقاييس
        st.subheader(f"🏢 {fund.get('company_name', symbol_input)} ({symbol_input})")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Current Price", f"${live.get('current_price', 0.0):,.2f}", f"{live.get('change_pct', 0.0)}%")
        m2.metric("P/E Ratio", f"{fund.get('pe_ratio', 'N/A')}")
        m3.metric("52-W High", f"${fund.get('52_week_high', 0.0):,.2f}")
        m4.metric("52-W Low", f"${fund.get('52_week_low', 0.0):,.2f}")

        # التنبؤ والتوصية
        st.divider()
        predictor = StockPricePredictor(df)
        pred_res = predictor.train_and_predict_next_day()

        rec = RecommendationEngine.get_final_recommendation(
            symbol=symbol_input,
            current_price=live.get('current_price', 0.0),
            rsi=tech.get('rsi_value', 50.0),
            pe=fund.get('pe_ratio') if fund.get('pe_ratio') else 20.0,
            margin=0.18,
            eps=fund.get('eps') if fund.get('eps') else 1.0,
            growth=0.08,
            trend=tech.get('trend', 'محايد')
        )

        st.info(f"💡 **AI Recommendation:** {rec['action_summary']}")

        # زر إرسال تنبيه Telegram
        if tg_token and tg_chat_id:
            if st.button("🔔 إرسال التوصية فوراً إلى Telegram"):
                notifier = AlertNotifier(tg_token, tg_chat_id)
                msg = f"🚨 *تنبيه ByToBy-Pro4*\n\n📈 *السهم:* {symbol_input}\n💵 *السعر الحالي:* ${live.get('current_price')}\n🎯 *التوصية:* {rec['rating']}\n📊 *RSI:* {tech.get('rsi_value')}"
                if notifier.send_telegram_alert(msg):
                    st.success("تم إرسال التنبيه بنجاح إلى تلجرام! 📲")
                else:
                    st.error("فشل إرسال التنبيه، تحقق من البيانات.")

        # الشارت التفاعلي المتقدم
        st.subheader("📈 Interactive Multi-Subplot Chart")
        fig = build_advanced_stock_chart(df, symbol_input)
        st.plotly_chart(fig, use_container_width=True)
