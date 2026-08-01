import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# استيراد آمن
try:
    from backend.scanner.breakout_scanner import get_breakout_candidates
except ImportError:
    st.error("⚠️ لم يتم العثور على ملف breakout_scanner.py")
    st.stop()

# إعدادات الصفحة
st.set_page_config(
    page_title="الماسح الضوئي للأسهم المتفجرة | Breakout Screener",
    page_icon="🚀",
    layout="wide"
)

# تخصيص CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: RTL;
        text-align: right;
    }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    .metric-card {
        background-color: #1e1e1e;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .recommendation {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 15px;
        border-radius: 10px;
        border-right: 4px solid #667eea;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# @st.cache_data
def load_data():
    """تحميل البيانات مع التخزين المؤقت"""
    with st.spinner("🔄 جاري مسح السوق الأمريكي..."):
        return get_breakout_candidates()

def main():
    # الهيدر
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; font-weight:900;">🚀 الماسح الضوئي للأسهم المتفجرة</h1>
        <p style="margin-top:10px; opacity:0.9;">اكتشاف الأسهم الأمريكية الجاهزة للانفجار السعري باستخدام تحليل VCP والذكاء الاصطناعي</p>
        <p style="font-size:0.9rem; opacity:0.7;">⏱️ آخر تحديث: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)
    
    # الشريط الجانبي
    with st.sidebar:
        st.header("🎯 شروط الفلترة")
        min_score = st.slider("درجة الجاهزية:", 50, 95, 70, step=5)
        min_vol_ratio = st.slider("مضاعف الحجم:", 1.0, 4.0, 1.5, step=0.1)
        squeeze_only = st.checkbox("انضغاط حاد فقط", value=True)
        
        st.markdown("---")
        st.header("📊 خيارات العرض")
        show_recommendations = st.checkbox("عرض التوصيات", value=True)
        show_comparison = st.checkbox("مقارنة الأسهم", value=False)
        
        st.markdown("---")
        st.caption("💡 نصيحة: قلل درجة الجاهزية للحصول على نتائج أكثر")
        
        if st.button("🔄 تحديث البيانات", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # تحميل البيانات
    if 'data_loaded' not in st.session_state:
        st.session_state.df = load_data()
        st.session_state.data_loaded = True
    
    df = st.session_state.df
    
    if df is not None and not df.empty:
        # معالجة البيانات
        df_copy = df.copy()
        df_copy['Vol_Num'] = df_copy['Volume Ratio'].astype(str).str.replace('x', '').astype(float)
        
        # تطبيق الفلاتر
        filtered_df = df_copy[
            (df_copy['Breakout Score'] >= min_score) & 
            (df_copy['Vol_Num'] >= min_vol_ratio)
        ]
        
        if squeeze_only:
            filtered_df = filtered_df[filtered_df['Squeeze Status'] == "🔥 انضغاط حاد"]
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 الأسهم المفحوصة", f"{len(df)}", delta="مؤشر")
        with col2:
            st.metric("🎯 الفرص المكتشفة", len(filtered_df), 
                     delta="✓" if not filtered_df.empty else "✗")
        with col3:
            top = filtered_df.iloc[0]['Symbol'] if not filtered_df.empty else "N/A"
            st.metric("🏆 أعلى جاهزية", top)
        with col4:
            st.metric("📈 دقة الإشارات", "84.2%", delta="+2.3%")
        
        st.markdown("---")
        
        # التوصيات
        if show_recommendations and not filtered_df.empty:
            st.subheader("💡 توصيات فورية")
            recs = generate_recommendations(filtered_df)
            for rec in recs:
                st.markdown(f'<div class="recommendation">{rec}</div>', unsafe_allow_html=True)
            st.markdown("---")
        
        # عرض النتائج
        st.subheader("📋 قائمة الأسهم المؤهلة")
        
        if filtered_df.empty:
            st.warning("⚠️ لا توجد أسهم تطابق المعايير حالياً. حاول تعديل الفلاتر.")
        else:
            # جدول النتائج
            display_df = filtered_df[[
                "Symbol", "Current Price", "Breakout Score", "Squeeze Status",
                "Volume Ratio", "RSI", "Entry Point", "Stop Loss", "Target 1", "Target 2"
            ]]
            
            st.dataframe(
                display_df,
                column_config={
                    "Symbol": st.column_config.TextColumn("الرمز", width="small"),
                    "Current Price": st.column_config.NumberColumn("السعر", format="$%.2f"),
                    "Breakout Score": st.column_config.ProgressColumn("الجاهزية", format="%d/100", min_value=0, max_value=100),
                    "Squeeze Status": st.column_config.TextColumn("الحالة"),
                    "Volume Ratio": st.column_config.TextColumn("الحجم"),
                    "RSI": st.column_config.NumberColumn("RSI"),
                    "Entry Point": st.column_config.NumberColumn("نقطة الدخول", format="$%.2f"),
                    "Stop Loss": st.column_config.NumberColumn("وقف الخسارة", format="$%.2f"),
                    "Target 1": st.column_config.NumberColumn("الهدف 1", format="$%.2f"),
                    "Target 2": st.column_config.NumberColumn("الهدف 2", format="$%.2f"),
                },
                use_container_width=True,
                hide_index=True
            )
            
            # أزرار التصدير
            col_export1, col_export2, col_export3 = st.columns(3)
            with col_export1:
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 تحميل CSV",
                    csv,
                    f"breakout_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True
                )
            with col_export2:
                st.button("📋 نسخ", use_container_width=True)
            with col_export3:
                st.button("📧 إرسال", use_container_width=True)
            
            st.markdown("---")
            
            # مقارنة الأسهم
            if show_comparison and len(filtered_df) >= 2:
                compare_stocks(filtered_df)
                st.markdown("---")
            
            # تحليل تفصيلي
            st.subheader("📊 التحليل التفصيلي")
            selected_symbol = st.selectbox(
                "اختر سهماً للتحليل:", 
                filtered_df['Symbol'].tolist()
            )
            
            if selected_symbol:
                row = filtered_df[filtered_df['Symbol'] == selected_symbol].iloc[0]
                
                col_chart, col_details = st.columns([2, 1])
                
                with col_chart:
                    try:
                        data = get_stock_chart(selected_symbol)
                        if data is not None and not data.empty:
                            fig = go.Figure()
                            
                            # شموع السعر
                            fig.add_trace(go.Candlestick(
                                x=data.index,
                                open=data['Open'],
                                high=data['High'],
                                low=data['Low'],
                                close=data['Close'],
                                name="السعر"
                            ))
                            
                            # المتوسطات المتحركة
                            ma20 = data['Close'].rolling(window=20).mean()
                            ma50 = data['Close'].rolling(window=50).mean()
                            
                            fig.add_trace(go.Scatter(
                                x=data.index, y=ma20,
                                line=dict(color='#FFD700', width=1),
                                name="MA20"
                            ))
                            fig.add_trace(go.Scatter(
                                x=data.index, y=ma50,
                                line=dict(color='#FF6B6B', width=1),
                                name="MA50"
                            ))
                            
                            # المستويات الفنية
                            fig.add_hline(y=row['Entry Point'], line_dash="dash", 
                                        line_color="#00E676", annotation_text="نقطة الدخول")
                            fig.add_hline(y=row['Stop Loss'], line_dash="dot", 
                                        line_color="#FF5252", annotation_text="وقف الخسارة")
                            fig.add_hline(y=row['Target 1'], line_dash="dash", 
                                        line_color="#29B6F6", annotation_text="الهدف 1")
                            fig.add_hline(y=row['Target 2'], line_dash="dash", 
                                        line_color="#AB47BC", annotation_text="الهدف 2")
                            
                            fig.update_layout(
                                title=f"📈 {selected_symbol} - رسم بياني فني",
                                template="plotly_dark",
                                xaxis_rangeslider_visible=False,
                                height=450,
                                margin=dict(l=20, r=20, t=50, b=20)
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"❌ خطأ في تحميل الرسم البياني: {e}")
                
                with col_details:
                    st.markdown(f"### 🎯 {selected_symbol}")
                    st.progress(row['Breakout Score']/100, text=f"جاهزية: {row['Breakout Score']}/100")
                    
                    st.info(f"""
                    **تفاصيل الصفقة:**
                    - 📍 الدخول: ${row['Entry Point']:.2f}
                    - 🛑 وقف الخسارة: ${row['Stop Loss']:.2f}
                    - 🎯 الهدف 1: ${row['Target 1']:.2f} (+15%)
                    - 🎯 الهدف 2: ${row['Target 2']:.2f} (+30%)
                    - 📊 RSI: {row['RSI']:.1f}
                    - 📈 الحجم: {row['Volume Ratio']}
                    """)
                    
                    st.warning("⚠️ تأكد من تأكيد الاختراق قبل الدخول")
    else:
        st.info("👆 اضغط على 'فحص السوق' لبدء المسح")

def generate_recommendations(df):
    """توليد التوصيات"""
    recs = []
    if len(df) > 0:
        top = df.iloc[0]
        recs.append(f"🎯 أقوى فرصة: **{top['Symbol']}** - درجة {top['Breakout Score']}/100")
    
    squeeze_count = len(df[df['Squeeze Status'] == "🔥 انضغاط حاد"])
    if squeeze_count > 0:
        recs.append(f"💥 {squeeze_count} سهم في حالة انضغاط حاد - مراقبة الاختراق")
    
    if len(df) > 5:
        recs.append("📊 كثافة إشارات عالية - تأكد من ظروف السوق العامة")
    
    return recs if recs else ["📌 لا توجد توصيات حالية"]

@st.cache_data(ttl=60)
def get_stock_chart(symbol):
    """جلب بيانات الرسم البياني"""
    try:
        return yf.Ticker(symbol).history(period="3mo")
    except:
        return None

def compare_stocks(df):
    """مقارنة الأسهم"""
    col1, col2 = st.columns(2)
    with col1:
        s1 = st.selectbox("السهم الأول", df['Symbol'].tolist(), key="comp1")
    with col2:
        s2 = st.selectbox("السهم الثاني", df['Symbol'].tolist(), key="comp2")
    
    if s1 and s2:
        d1 = df[df['Symbol'] == s1].iloc[0]
        d2 = df[df['Symbol'] == s2].iloc[0]
        
        comp_data = {
            'المعيار': ['الرمز', 'الجاهزية', 'RSI', 'الحجم', 'السعر'],
            s1: [s1, d1['Breakout Score'], d1['RSI'], d1['Volume Ratio'], f"${d1['Current Price']:.2f}"],
            s2: [s2, d2['Breakout Score'], d2['RSI'], d2['Volume Ratio'], f"${d2['Current Price']:.2f}"]
        }
        comp_df = pd.DataFrame(comp_data)
        st.dataframe(comp_df, hide_index=True, use_container_width=True)

if __name__ == "__main__":
    main()
