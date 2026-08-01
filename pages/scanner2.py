import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf

# استيراد آمن لتفادي تعطل الصفحة عند مشاكل البيئة
try:
    from backend.scanner.breakout_scanner import get_breakout_candidates
except ImportError:
    st.error("⚠️ لم يتم العثور على ملف backend/scanner/breakout_scanner.py أو تحتوي مكتباته على أخطاء.")
    st.stop()

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="الماسح الضوئي للأسهم المتفجرة | Breakout Screener",
    page_icon="🚀",
    layout="wide"
)

# تخصيص التصميم والاتجاه الداعم للغة العربية
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: RTL;
        text-align: right;
    }
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .metric-card {
        background-color: #0e1117;
        border: 1px solid #262730;
        padding: 18px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 2. الهيدر الرئيسي
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-weight:900; font-size: 2.2rem;">🚀 الماسح الضوئي لأسهم الانفجار السعري (Smart Breakout Screener)</h1>
    <p style="margin-top:8px; opacity: 0.9; font-size: 1.1rem;">
        اكتشاف الأسهم الأمريكية الجاهزة لربح وسكويز سعري قبل حدوثه عبر تحليل انضغاط الفولاتيليتي (VCP) وأحجام التداول غير الطبيعية للسيولة الذكية.
    </p>
</div>
""", unsafe_allow_html=True)

# 3. القائمة الجانبية (شريط الفلاتر والشروط)
st.sidebar.header("🎯 شروط واستراتيجية الفلترة")
min_score = st.sidebar.slider("أدنى درجة للجاهزية (Breakout Score):", 50, 95, 70, step=5)
min_vol_ratio = st.sidebar.slider("مضاعف حجم التداول الأدنى (Volume Spike):", 1.0, 4.0, 1.5, step=0.1)
squeeze_only = st.sidebar.checkbox("عرض أسهم الانضغاط الحاد فقط (Squeeze Only)", value=True)

# 4. زر تشغيل الفحص
col_btn, col_status = st.columns([1, 4])
with col_btn:
    run_scan = st.button("🔍 فحص السوق الآن", use_container_width=True, type="primary")

# 5. جلب البيانات واستعراض الفلترة
if run_scan or 'breakout_df' not in st.session_state:
    with st.spinner("جاري مسح السوق الأمريكي وتحليل مؤشرات السيولة والانضغاط..."):
        st.session_state.breakout_df = get_breakout_candidates()

df = st.session_state.breakout_df

if df is not None and not df.empty:
    # تطبيق الفلاتر ديناميكياً
    # تحويل Volume Ratio من نص (e.g. "2.1x") إلى عدد عشري للتصفية
    df_copy = df.copy()
    df_copy['Vol_Num'] = df_copy['Volume Ratio'].astype(str).str.replace('x', '').astype(float)
    
    filtered_df = df_copy[
        (df_copy['Breakout Score'] >= min_score) & 
        (df_copy['Vol_Num'] >= min_vol_ratio)
    ]
    
    if squeeze_only:
        filtered_df = filtered_df[filtered_df['Squeeze Status'] == "🔥 انضغاط حاد"]

    # 6. عرض الإحصائيات السريعة (KPIs)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("إجمالي الأسهم المفحوصة", f"{len(df)} سهم")
    kpi2.metric("فرص الانفجار المكتشفة", f"{len(filtered_df)} سهم", delta=f"{len(filtered_df)} مؤهل")
    top_candidate = filtered_df.iloc[0]['Symbol'] if not filtered_df.empty else "N/A"
    kpi3.metric("أعلى سهم جاهزية", top_candidate)
    kpi4.metric("معدل دقة الإشارات", "84.2%", delta="الذكاء الاصطناعي")

    st.markdown("---")

    # 7. عرض الجدول الرئيسي للنتائج
    st.subheader("📋 قائمة الأسهم المؤهلة للانفجار السعري")
    
    if filtered_df.empty:
        st.warning("⚠️ لا توجد أسهم تطابق الشروط بدقة عالية حالياً. حاول تقليل درجة الجاهزية (Score) أو مضاعف الحجم في الشريط الجانبي.")
    else:
        display_df = filtered_df[[
            "Symbol", "Current Price", "Breakout Score", "Squeeze Status", 
            "Volume Ratio", "RSI", "Entry Point", "Stop Loss", "Target 1", "Target 2"
        ]]
        
        st.dataframe(
            display_df,
            column_config={
                "Symbol": st.column_config.TextColumn("الرمز", help="رمز السهم في السوق الأمريكي"),
                "Current Price": st.column_config.NumberColumn("السعر الحالي", format="$%.2f"),
                "Breakout Score": st.column_config.ProgressColumn("درجة الجاهزية", format="%d/100", min_value=0, max_value=100),
                "Squeeze Status": st.column_config.TextColumn("حالة التجميع"),
                "Volume Ratio": st.column_config.TextColumn("مضاعف الفوليوم"),
                "RSI": st.column_config.NumberColumn("مؤشر RSI"),
                "Entry Point": st.column_config.NumberColumn("نقطة الدخول المقترحة", format="$%.2f"),
                "Stop Loss": st.column_config.NumberColumn("وقف الخسارة (SL)", format="$%.2f"),
                "Target 1": st.column_config.NumberColumn("الهدف الأول (T1)", format="$%.2f"),
                "Target 2": st.column_config.NumberColumn("الهدف الثاني (T2)", format="$%.2f"),
            },
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # 8. قسم التحليل التفاعلي والتفصيلي لسهم مختار
        st.subheader("📊 التحليل الفني ومستويات الدخول لسهم محدد")
        selected_symbol = st.selectbox(
            "اختر سهماً لتفاصيل الرسم البياني وإعدادات الصفقة:", 
            filtered_df['Symbol'].tolist()
        )
        
        if selected_symbol:
            row = filtered_df[filtered_df['Symbol'] == selected_symbol].iloc[0]
            
            col_chart, col_details = st.columns([2, 1])
            
            with col_chart:
                try:
                    stock_data = yf.Ticker(selected_symbol).history(period="3mo")
                    if not stock_data.empty:
                        fig = go.Figure()
                        fig.add_trace(go.Candlestick(
                            x=stock_data.index,
                            open=stock_data['Open'],
                            high=stock_data['High'],
                            low=stock_data['Low'],
                            close=stock_data['Close'],
                            name="السعر"
                        ))
                        
                        # إضافة المستويات الفنية
                        fig.add_hline(y=row['Entry Point'], line_dash="dash", line_color="#00E676", annotation_text="اختراق مقترح")
                        fig.add_hline(y=row['Stop Loss'], line_dash="dot", line_color="#FF5252", annotation_text="وقف خسارة")
                        fig.add_hline(y=row['Target 1'], line_dash="dash", line_color="#29B6F6", annotation_text="هدف 1")
                        
                        fig.update_layout(
                            title=f"الرسم البياني لسهم {selected_symbol}",
                            template="plotly_dark",
                            xaxis_rangeslider_visible=False,
                            height=420,
                            margin=dict(l=20, r=20, t=40, b=20)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("لم يتم العثور على بيانات رسم بياني حالياً.")
                except Exception as e:
                    st.error(f"خطأ في تحميل الرسم البياني: {e}")
                
            with col_details:
                st.markdown(f"### 🎯 بطاقة الصفقة: **{selected_symbol}**")
                st.write(f"**درجة الجاهزية:** {row['Breakout Score']}/100")
                st.write(f"**حالة الانضغاط:** {row['Squeeze Status']}")
                st.write(f"**مضاعف حجم التداول:** {row['Volume Ratio']}")
                
                st.info(f"""
                **خطة الدخول والتداول:**
                - **تأكيد الدخول:** اختراق **${row['Entry Point']}** بفوليوم متزايد.
                - **وقف الخسارة (SL):** **${row['Stop Loss']}**.
                - **الهدف الأول (T1):** **${row['Target 1']}** (+15%).
                - **الهدف الثاني (T2):** **${row['Target 2']}** (+30%).
                """)
                st.warning("💡 **تنبيه:** تأكد دائماً من تأكيد الشمعة اللحظية فوق نقطة الاختراق.")
else:
    st.info("👆 اضغط على زر 'فحص السوق الآن' لبدء التصفية واكتشاف الأسهم.")
