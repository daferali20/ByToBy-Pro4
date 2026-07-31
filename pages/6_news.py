# pages/6_news.py

import streamlit as st
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.config import US_STOCK_WATCHLIST
from backend.news.news_provider import USNewsProvider

st.title("📰 US Live Market News | التغذية الإخبارية للأسهم الأمريكية")

news_provider = USNewsProvider()

# شريط خيارات الفلترة
col_filter1, col_filter2 = st.columns([2, 1])

with col_filter1:
    view_mode = st.radio(
        "نطاق التغطية الإخبارية:",
        ["تغذية عامة للسوق الأمريكي (Market-Wide)", "تخصيص سهم أمريكي محدد (Specific Ticker)"],
        horizontal=True
    )

if view_mode == "تخصيص سهم أمريكي محدد (Specific Ticker)":
    selected_symbol = st.selectbox("اختر الرمز الأمريكي:", US_STOCK_WATCHLIST, index=0)
    
    if st.button("تحديث أخبار السهم"):
        st.rerun()

    with st.spinner(f"جاري جلب الأخبار الحية لسهم {selected_symbol}..."):
        news_items = news_provider.get_stock_news(selected_symbol, limit=8)
else:
    with st.spinner("جاري جلب آخر أخبار شركات S&P 500 و NASDAQ..."):
        # جلب أخبار القائمة المعتمدة في Config
        news_items = news_provider.get_market_wide_us_news(US_STOCK_WATCHLIST[:8], limit_per_stock=1)

st.divider()

# عرض الأخبار المفلترة
if not news_items:
    st.warning("⚠️ لا توجد أخبار حية متاحة حالياً للرمز المختار.")
else:
    st.subheader(f"📊 إجمالي الأخبار المجلوبة: {len(news_items)}")
    
    for item in news_items:
        with st.container():
            c1, c2 = st.columns([4, 1])
            
            with c1:
                st.markdown(f"### [{item['title']}]({item['link']})")
                st.caption(f"🏢 **الرمز:** `{item['symbol']}` | 📰 **المصدر:** {item['publisher']} | ⏱️ **الوقت:** {item['published_at']}")
            
            with c2:
                st.metric(label="تحليل AI للشعور", value=item['sentiment'])

            st.divider()
