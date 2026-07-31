import streamlit as st
import sys, os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.scanner.screener import SmartScanner

st.title("🔍 الماسح الذكي للأسهم")

# خيارات التصفية من الواجهة
rsi_range = st.slider("نطاق مؤشر القوة النسبية (RSI)", 0, 100, (30, 70))
trend_filter = st.radio("الاتجاه المطلوب", ["الكل", "صاعد", "هابط"], horizontal=True)

# قائمة الأسهم المراد مسحها
watchlist = ["2222.SR", "1120.SR", "2010.SR", "7010.SR", "AAPL", "NVDA"]

if st.button("بدء المسح"):
    with st.spinner("جاري مسح الأسهم المطابقة للشرط..."):
        scanner = SmartScanner(watchlist)
        results = scanner.scan_market(
            min_rsi=rsi_range[0],
            max_rsi=rsi_range[1],
            trend_filter=trend_filter
        )
        
        if results:
            df_results = pd.DataFrame(results)
            df_results.columns = ["الرمز", "إغلاق", "RSI", "الاتجاه", "إشارة MACD"]
            st.dataframe(df_results, use_container_width=True)
        else:
            st.warning("لا توجد أسهم تطابق الشروط المحددة حالياً.")
