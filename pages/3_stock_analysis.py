import streamlit as st
import sys, os
import plotly.graph_objects as go

# ضمان العثور على مجلدات backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.stock_service import StockService

st.title("🔬 التحليل الفني الشامل")

symbol = st.text_input("أدخل رمز السهم:", value="2222.SR")

# استخدام st.cache_data لمنع إعادة تحميل البيانات مع كل تغيير بسيط
@st.cache_data(ttl=300) # التحديث كل 5 دقائق
def fetch_analysis(sym):
    return StockService.get_full_analysis(sym)

if symbol:
    with st.spinner("جاري جلب البيانات وتحليل المؤشرات..."):
        analysis = fetch_analysis(symbol)

    if "error" in analysis:
        st.error(analysis["error"])
    else:
        st.subheader(f"الشركة: {analysis['company_name']}")
        
        # عرض نتائج التقييم الفني
        tech = analysis["technical_summary"]
        col1, col2, col3 = st.columns(3)
        col1.metric("السعر الحالي", f"{analysis['current_price']} SAR")
        col2.metric("الاتجاه الفني", tech["trend"])
        col3.metric("مؤشر RSI", f"{tech['rsi_value']} ({tech['rsi_status']})")

        # النماذج الفنية المكتشفة
        patterns = analysis["patterns"]
        st.write("---")
        st.write("### 📌 النماذج الفنية المكتشفة:")
        st.caption(f"- شمعة ابتلاعية شرائية: {'نعم 🟢' if patterns['bullish_engulfing'] else 'لا ⚪'}")
        st.caption(f"- اختراق قمة 20 يوم: {'نعم 🟢' if patterns['breakout_20d'] else 'لا ⚪'}")

        # رسم البيانات التاريخية
        df = analysis["raw_data"]
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']
        )])
        fig.update_layout(template="plotly_dark", height=450)
        st.plotly_chart(fig, use_container_width=True)
