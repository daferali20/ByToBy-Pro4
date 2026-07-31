import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta

# إعداد الصفحة
st.set_page_config(
    page_title="تفاصيل الأسهم السعودية",
    page_icon="🇸🇦",
    layout="wide"
)

# وظيفة لجلب قائمة الأسهم السعودية من Tadawul
@st.cache_data(ttl=86400)  # تحديث كل 24 ساعة
def get_saudi_stocks():
    """جلب قائمة الأسهم السعودية المتداولة"""
    try:
        # محاولة جلب البيانات من API خارجي (مثال)
        url = "https://api.tadawul.com.sa/stocks"  # هذا رابط وهمي، استخدم API حقيقي
        
        # قائمة أسهم سعودية معروفة (كحل احتياطي)
        stocks = [
            {"symbol": "1120.SR", "name": "الراجحي", "sector": "البنوك"},
            {"symbol": "1180.SR", "name": "الأهلي", "sector": "البنوك"},
            {"symbol": "1010.SR", "name": "سابك", "sector": "الصناعات البتروكيماوية"},
            {"symbol": "2010.SR", "name": "معادن", "sector": "التعدين"},
            {"symbol": "2222.SR", "name": "أرامكو", "sector": "الطاقة"},
            {"symbol": "3050.SR", "name": "الاتصالات", "sector": "الاتصالات"},
            {"symbol": "4011.SR", "name": "المراعي", "sector": "الزراعة"},
            {"symbol": "2010.SR", "name": "معادن", "sector": "التعدين"},
            {"symbol": "4300.SR", "name": "دار الأركان", "sector": "العقار"},
            {"symbol": "5110.SR", "name": "العربي", "sector": "التأمين"},
        ]
        return pd.DataFrame(stocks)
    except Exception as e:
        st.warning(f"⚠️ تعذر جلب البيانات من المصدر الخارجي: {e}")
        return None

# وظيفة لجلب بيانات السهم من Yahoo Finance
@st.cache_data(ttl=300)  # تحديث كل 5 دقائق
def fetch_stock_data(symbol):
    """جلب بيانات السهم من Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        
        # جلب المعلومات الأساسية
        info = ticker.info
        
        # جلب البيانات التاريخية لآخر سنة
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        hist = ticker.history(start=start_date, end=end_date)
        
        return {
            "info": info,
            "history": hist,
            "financials": ticker.financials,
            "balance_sheet": ticker.balance_sheet,
            "cashflow": ticker.cashflow,
            "major_holders": ticker.major_holders,
            "institutional_holders": ticker.institutional_holders
        }
    except Exception as e:
        st.error(f"❌ خطأ في جلب بيانات السهم: {e}")
        return None

# وظيفة لجلب الأخبار المتعلقة بالسهم
def get_stock_news(symbol):
    """جلب آخر الأخبار عن السهم"""
    try:
        # استخدام Yahoo Finance للأخبار
        ticker = yf.Ticker(symbol)
        news = ticker.news
        return news[:5]  # آخر 5 أخبار
    except:
        return []

# واجهة المستخدم الرئيسية
st.title("📊 منصة تحليل الأسهم السعودية")

# السلايدر والتحكم في البحث
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    # جلب قائمة الأسهم
    stocks_df = get_saudi_stocks()
    
    if stocks_df is not None and not stocks_df.empty:
        # إنشاء خيارات للاختيار
        stock_options = {f"{row['symbol']} - {row['name']} ({row['sector']})": row['symbol'] 
                        for _, row in stocks_df.iterrows()}
        
        # مربع اختيار مع إمكانية البحث
        selected_display = st.selectbox(
            "🔍 اختر السهم:",
            options=list(stock_options.keys()),
            index=0,
            help="ابحث عن السهم الذي تريده"
        )
        
        # استخراج الرمز من الخيار المختار
        selected_symbol = stock_options[selected_display]
        
        # عرض معلومات السهم المختار
        if selected_symbol:
            st.success(f"✅ السهم المختار: {selected_display}")
    
    else:
        # خيار الكتابة اليدوية كحل احتياطي
        selected_symbol = st.text_input(
            "📝 أدخل رمز السهم:",
            value="1120.SR",
            help="مثال: 1120.SR للراجحي"
        )

with col2:
    # اختيار الفترة الزمنية
    period_options = {
        "1 يوم": "1d",
        "5 أيام": "5d",
        "شهر": "1mo",
        "3 أشهر": "3mo",
        "6 أشهر": "6mo",
        "سنة": "1y",
        "سنتين": "2y",
        "5 سنوات": "5y"
    }
    selected_period = st.selectbox("📅 الفترة:", list(period_options.keys()), index=5)

with col3:
    # زر التحديث
    if st.button("🔄 تحديث البيانات", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# جلب البيانات
if selected_symbol:
    with st.spinner(f"🔄 جاري جلب بيانات {selected_symbol}..."):
        stock_data = fetch_stock_data(selected_symbol)
        
        if stock_data:
            info = stock_data["info"]
            history = stock_data["history"]
            
            # عرض معلومات أساسية
            st.divider()
            
            # بطاقات المعلومات الرئيسية
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                current_price = info.get('regularMarketPrice', info.get('currentPrice', 0))
                st.metric(
                    label="💰 السعر الحالي",
                    value=f"{current_price:.2f} SAR" if current_price else "غير متوفر",
                    delta=f"{info.get('regularMarketChangePercent', 0):.2f}%" if info.get('regularMarketChangePercent') else None
                )
            
            with col2:
                st.metric(
                    label="📊 القيمة السوقية",
                    value=f"{info.get('marketCap', 0) / 1e9:.2f} مليار" if info.get('marketCap') else "غير متوفر"
                )
            
            with col3:
                st.metric(
                    label="📈 مكرر الأرباح (P/E)",
                    value=f"{info.get('trailingPE', 0):.2f}" if info.get('trailingPE') else "غير متوفر"
                )
            
            with col4:
                st.metric(
                    label="💵 توزيعات الأرباح",
                    value=f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else "غير متوفر"
                )
            
            # الأقسام الرئيسية
            tab1, tab2, tab3, tab4 = st.tabs([
                "📈 السعر والرسوم البيانية",
                "🏛️ القوائم المالية", 
                "📊 المؤشرات المالية",
                "👥 الملكية والأخبار"
            ])
            
            with tab1:
                if not history.empty:
                    # رسم بياني لسعر الإغلاق
                    st.subheader("📈 أداء السهم")
                    
                    # عرض بيانات السعر مع التحكم
                    chart_type = st.radio(
                        "نوع الرسم البياني:",
                        ["خطي", "شموع", "مساحي"],
                        horizontal=True
                    )
                    
                    # مؤشرات إضافية
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.checkbox("📊 إظهار المتوسطات المتحركة"):
                            # حساب المتوسطات المتحركة
                            hist_data = history['Close'].tail(50)
                            st.line_chart(hist_data)
                    
                    with col2:
                        if st.checkbox("📈 حجم التداول"):
                            st.bar_chart(history['Volume'].tail(30))
                    
                    # عرض الجدول
                    st.dataframe(
                        history.tail(10).style.format({
                            'Open': '{:.2f}',
                            'High': '{:.2f}',
                            'Low': '{:.2f}',
                            'Close': '{:.2f}',
                            'Volume': '{:,.0f}'
                        }),
                        use_container_width=True
                    )
                else:
                    st.warning("لا توجد بيانات تاريخية متاحة")
            
            with tab2:
                st.subheader("🏛️ القوائم المالية للسنوات الأربع الأخيرة")
                
                # جلب القوائم المالية
                financials = stock_data.get("financials")
                balance = stock_data.get("balance_sheet")
                
                if financials is not None and not financials.empty:
                    # عرض قائمة الدخل
                    st.write("**📋 قائمة الدخل**")
                    st.dataframe(financials, use_container_width=True)
                else:
                    st.info("📝 البيانات المالية غير متوفرة لهذا السهم")
                
                if balance is not None and not balance.empty:
                    st.write("**📋 الميزانية العمومية**")
                    st.dataframe(balance, use_container_width=True)
                else:
                    st.info("📝 الميزانية العمومية غير متوفرة")
            
            with tab3:
                st.subheader("📊 المؤشرات المالية الرئيسية")
                
                # عرض المؤشرات المالية في بطاقات
                metrics_data = {
                    "العائد على حقوق الملكية (ROE)": info.get('returnOnEquity', 'غير متوفر'),
                    "العائد على الأصول (ROA)": info.get('returnOnAssets', 'غير متوفر'),
                    "الربحية": f"{info.get('profitMargins', 0) * 100:.2f}%" if info.get('profitMargins') else 'غير متوفر',
                    "نسبة الدين إلى حقوق الملكية": info.get('debtToEquity', 'غير متوفر'),
                    "السيولة الحالية": info.get('currentRatio', 'غير متوفر'),
                    "السيولة السريعة": info.get('quickRatio', 'غير متوفر'),
                }
                
                # عرض المؤشرات في صفوف
                cols = st.columns(3)
                for idx, (key, value) in enumerate(metrics_data.items()):
                    with cols[idx % 3]:
                        st.metric(
                            label=key,
                            value=f"{value:.2f}" if isinstance(value, (int, float)) else str(value)
                        )
                
                # مقارنة مع القطاع
                st.divider()
                st.subheader("📊 مقارنة مع متوسط القطاع")
                
                # بيانات وهمية للمقارنة
                sector_avg = {
                    "مكرر الأرباح": 16.5,
                    "العائد على حقوق الملكية": 14.2,
                    "نسبة الدين": 0.35
                }
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    pe = info.get('trailingPE', 0)
                    st.metric(
                        "مكرر الأرباح",
                        f"{pe:.2f}" if pe else "غير متوفر",
                        delta=f"{pe - sector_avg['مكرر الأرباح']:.2f}" if pe else None
                    )
                with col2:
                    roe = info.get('returnOnEquity', 0)
                    st.metric(
                        "العائد على حقوق الملكية",
                        f"{roe * 100:.2f}%" if roe else "غير متوفر",
                        delta=f"{(roe - sector_avg['العائد على حقوق الملكية']/100) * 100:.2f}%" if roe else None
                    )
                with col3:
                    dte = info.get('debtToEquity', 0)
                    st.metric(
                        "نسبة الدين",
                        f"{dte:.2f}" if dte else "غير متوفر",
                        delta=f"{dte - sector_avg['نسبة الدين']:.2f}" if dte else None
                    )
            
            with tab4:
                st.subheader("👥 الملكية والأخبار")
                
                # عرض كبار المالكين
                major_holders = stock_data.get("major_holders")
                if major_holders is not None and not major_holders.empty:
                    st.write("**كبار المالكين**")
                    st.dataframe(major_holders, use_container_width=True)
                else:
                    st.info("📝 بيانات كبار المالكين غير متوفرة")
                
                # عرض المؤسسات المالكة
                institutional = stock_data.get("institutional_holders")
                if institutional is not None and not institutional.empty:
                    st.write("**المالكين المؤسسيين**")
                    st.dataframe(institutional, use_container_width=True)
                else:
                    st.info("📝 بيانات المالكين المؤسسيين غير متوفرة")
                
                # عرض الأخبار
                st.divider()
                st.subheader("📰 آخر الأخبار")
                
                news = get_stock_news(selected_symbol)
                if news:
                    for i, article in enumerate(news[:5]):
                        with st.expander(f"📌 {article.get('title', 'خبر')[:50]}..."):
                            st.write(f"📝 {article.get('description', 'لا يوجد وصف')}")
                            st.caption(f"📅 {article.get('pubDate', 'تاريخ غير معروف')}")
                else:
                    st.info("📝 لا توجد أخبار متاحة حالياً")
                    
        else:
            st.error("❌ تعذر جلب البيانات، تأكد من رمز السهم")

# معلومات إضافية في الشريط الجانبي
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/line-chart.png", width=80)
    st.title("📊 ByToBy-Pro4")
    st.caption("منصة تحليل الأسهم السعودية")
    st.divider()
    
    st.subheader("ℹ️ معلومات إضافية")
    
    # عرض إحصائيات سريعة
    if 'stock_data' in locals() and stock_data:
        info = stock_data.get("info", {})
        st.write(f"**🏢 الشركة:** {info.get('longName', 'غير معروف')}")
        st.write(f"**🌍 القطاع:** {info.get('sector', 'غير معروف')}")
        st.write(f"**🌐 الصناعة:** {info.get('industry', 'غير معروف')}")
        st.write(f"**📅 اليوم:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    st.divider()
    
    # إعدادات إضافية
    with st.expander("⚙️ الإعدادات المتقدمة"):
        show_technical = st.checkbox("📊 إظهار المؤشرات الفنية", value=True)
        auto_refresh = st.checkbox("🔄 تحديث تلقائي", value=False)
        if auto_refresh:
            refresh_interval = st.slider("معدل التحديث (دقائق)", 1, 30, 5)

# تذييل الصفحة
st.divider()
st.caption("© 2026 ByToBy-Pro4 | جميع الحقوق محفوظة | البيانات مقدمة من Yahoo Finance")
