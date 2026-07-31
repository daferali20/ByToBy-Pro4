import streamlit as st

st.title("📰 الأخبار والتحليل الإخباري | Market News")

news_list = [
    {"title": "نتائج أرباح أرامكو تتجاوز التوقعات للنصف الأول", "time": "قبل ساعتين", "sentiment": "إيجابي 🟢"},
    {"title": "الفيدرالي يثبت أرقام الفائدة مع إشارات لخفض قريب", "time": "قبل 4 ساعات", "sentiment": "إيجابي 🟢"},
    {"title": "تذبذب أسعار النفط بسبب المخاوف الجيوسياسية", "time": "قبل 6 ساعات", "sentiment": "محايد ⚪"}
]

for news in news_list:
    st.markdown(f"### {news['title']}")
    st.caption(f"⏱️ {news['time']} | 🧠 تحليل الشعور: **{news['sentiment']}**")
    st.write("تفاصيل الخبر والمعطيات التي يحللها نظام ByToBy-Pro4 لمعرفة مدى تأثيرها على حركة الأسهم...")
    st.divider()
