import streamlit as st

st.title("🔔 نظام التنبيهات الذكي | Smart Alerts")

st.subheader("➕ إضافة تنبيه جديد")
col1, col2, col3 = st.columns(3)
with col1:
    symbol = st.text_input("رمز السهم", "1120.SR")
with col2:
    condition = st.selectbox("الشرط", ["يتجاوز سعر", "ينخفض عن سعر", "RSI يتجاوز 70"])
with col3:
    target = st.number_input("القيمة المستهدفة", value=90.0)

if st.button("تفعيل التنبيه"):
    st.success(f"تم إنشاء التنبيه للسهم {symbol} عند تحقق شرط: {condition} {target}")
