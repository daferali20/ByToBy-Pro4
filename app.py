import streamlit as st
import os

# مسار ملف الـ CSS
css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
  with open(css_path, "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
st.set_page_config(
    page_title="ByToBy-Pro4 | منصة تحليل الأسهم Smart Stock Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional Dark/Light UI
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: bold; color: #1E88E5; text-align: center; margin-bottom: 20px; }
    .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 8px; border-left: 5px solid #1E88E5; }
    div[data-testid="stSidebarNav"] { font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)

st.sidebar.image("https://img.icons8.com/color/96/000000/line-chart.png", width=80)
st.sidebar.title(" ByToBy-Pro4")
st.sidebar.caption("الجيل الرابع لمنصة التحليل المالي والذكاء الاصطناعي")
st.sidebar.divider()

st.title("🚀 مرحباً بك في نظام ByToBy-Pro4")
st.info("👈 اختر الصفحة المطلوبة من القائمة الجانبية للبدء في استخدام الأدوات والتحليلات.")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("الحالة التشغيلية للنظام", "نشط 🟢", "100% Up")
with col2:
    st.metric("الأسواق المتاحة", "تداول (TASI) + US Markets", "+10,000 سهم")
with col3:
    st.metric("نموذج AI", "ByToBy-Predict v4", "دقة 89.4%")
