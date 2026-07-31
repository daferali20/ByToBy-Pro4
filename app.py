import os
import sys
import streamlit as st

# 1. ضبط مسار الجذر للمشروع أولاً
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# 2. أمر التهيئة الأول والوحيد لـ Streamlit في بداية الصفحة
st.set_page_config(
    page_title="ByToBy-Pro4 | منصة تحليل الأسهم Smart Stock Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 3. تحميل ملف الـ CSS الخارجي بعد st.set_page_config
css_path = os.path.join(ROOT_DIR, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 4. تنسيق إضافي ناعم ومتوافق مع المظهر الداكن/المضيء بوضوح تام
st.markdown("""
<style>
    .main-header { 
        font-size: 2.2rem; 
        font-weight: 700; 
        color: #58a6ff; 
        text-align: center; 
        margin-bottom: 25px; 
    }
    div[data-testid="stSidebarNav"] { 
        font-size: 1.1rem; 
    }
</style>
""", unsafe_allow_html=True)

# القائمة الجانبية (Sidebar)
st.sidebar.image("https://img.icons8.com/color/96/000000/line-chart.png", width=80)
st.sidebar.title("ByToBy-Pro4")
st.sidebar.caption("الجيل الرابع لمنصة التحليل المالي والذكاء الاصطناعي")
st.sidebar.divider()

# المحتوى الرئيسي
st.markdown('<div class="main-header">🚀 مرحباً بك في نظام ByToBy-Pro4</div>', unsafe_allow_html=True)
st.info("👈 اختر الصفحة المطلوبة من القائمة الجانبية للبدء في استخدام الأدوات والتحليلات المتقدمة.")

st.divider()

# بطاقات العرض مع ألوان واضحة للخطوط
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="الحالة التشغيلية للنظام", 
        value="نشط 🟢", 
        delta="100% Up"
    )

with col2:
    st.metric(
        label="الأسواق المتاحة", 
        value="US Markets", 
        delta="+10,000 stocks"
    )

with col3:
    st.metric(
        label="نموذج الذكاء الاصطناعي", 
        value="ByToBy-Predict v4", 
        delta="Acc. 89.4%"
    )
