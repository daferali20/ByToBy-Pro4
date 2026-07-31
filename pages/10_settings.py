import streamlit as st
import os

# مسار ملف الـ CSS
css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
  with open(css_path, "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
st.title("⚙️ الإعدادات | Settings")

st.subheader("تفضيلات النظام")
st.toggle("تفعيل التحديث اللحظي للأسعار (Websocket)", value=True)
st.toggle("التنبيهات عبر البريد / Telegram", value=False)
st.selectbox("لغة الواجهة", ["العربية", "English"])

st.button("حفظ التغييرات")
