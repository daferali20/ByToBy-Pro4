import streamlit as st

st.title("⚙️ الإعدادات | Settings")

st.subheader("تفضيلات النظام")
st.toggle("تفعيل التحديث اللحظي للأسعار (Websocket)", value=True)
st.toggle("التنبيهات عبر البريد / Telegram", value=False)
st.selectbox("لغة الواجهة", ["العربية", "English"])

st.button("حفظ التغييرات")
