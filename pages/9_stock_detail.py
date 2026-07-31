import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# إعداد الصفحة
st.set_page_config(
    page_title="📊 منصة تحليل الأسهم الأمريكية | US Stocks",
    page_icon="🇺🇸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تحميل CSS مخصص
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 20px;
    }
    .stock-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 10px 0;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 5px;
    }
    .green-text {
        color: #00cc00;
    }
    .red-text {
        color: #ff3333;
    }
</style>
""", unsafe_allow_html=True)

# وظيفة لجلب قائمة الأسهم الأمريكية الشهيرة
@st.cache_data(ttl=86400)
def get_us_stocks():
    """جلب قائمة الأسهم الأمريكية الشهيرة"""
    stocks = {
        "AAPL": "Apple Inc.",
        "MSFT": "Microsoft Corporation",
        "GOOGL": "Alphabet Inc.",
        "AMZN": "Amazon.com Inc.",
        "NVDA": "NVIDIA Corporation",
        "META": "Meta Platforms Inc.",
        "TSLA": "Tesla Inc.",
        "JPM": "JPMorgan Chase & Co.",
        "V": "Visa Inc.",
        "WMT": "Walmart Inc.",
        "JNJ": "Johnson & Johnson",
        "PG": "Procter & Gamble Co.",
        "UNH": "UnitedHealth Group Inc.",
        "HD": "Home Depot Inc.",
        "MA": "Mastercard Inc.",
        "DIS": "Walt Disney Co.",
        "NFLX": "Netflix Inc.",
        "ADBE": "Adobe Inc.",
        "CRM": "Salesforce Inc.",
        "AMD": "Advanced Micro Devices Inc.",
        "INTC": "Intel Corporation",
        "PFE": "Pfizer Inc.",
        "TMO": "Thermo Fisher Scientific",
        "ABT": "Abbott Laboratories",
        "NKE": "Nike Inc.",
        "COST": "Costco Wholesale",
        "CVX": "Chevron Corporation",
        "XOM": "Exxon Mobil Corporation",
        "BAC": "Bank of America",
        "WFC": "Wells Fargo & Co.",
        "KO": "Coca-Cola Co.",
        "PEP": "PepsiCo Inc.",
        "MCD": "McDonald's Corp.",
        "SBUX": "Starbucks Corp.",
        "TXN": "Texas Instruments",
        "QCOM": "Qualcomm Inc.",
        "AVGO": "Broadcom Inc.",
        "CSCO": "Cisco Systems Inc.",
        "ORCL": "Oracle Corporation",
        "IBM": "International Business Machines"
    }
    return pd.DataFrame(list(stocks.items()), columns=['symbol', 'name'])

# وظيفة لجلب بيانات السهم
@st.cache_data(ttl=300)
def fetch_stock_data(symbol, period="1y"):
    """جلب بيانات السهم من Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        
        # جلب البيانات التاريخية
        end_date = datetime.now()
        if period == "1d":
            start_date = end_date - timedelta(days=1)
        elif period == "5d":
            start_date = end_date - timedelta(days=5)
        elif period == "1mo":
            start_date = end_date - timedelta(days=30)
        elif period == "3mo":
            start_date = end_date - timedelta(days=90)
        elif period == "6mo":
            start_date = end_date - timedelta(days=180)
        elif period == "1y":
            start_date = end_date - timedelta(days=365)
        elif period == "2y":
            start_date = end_date - timedelta(days=730)
        elif period == "5y":
            start_date = end_date - timedelta(days=1825)
        else:
            start_date = end_date - timedelta(days=365)
        
        hist = ticker.history(start=start_date, end=end_date)
        
        # جلب المعلومات الأساسية
        info = ticker.info
        
        # جلب البيانات المالية
        financials = ticker.financials
        balance_sheet = ticker.balance_sheet
        cashflow = ticker.cashflow
        
        # جلب بيانات المؤسسات
        major_holders = ticker.major_holders
        institutional_holders = ticker.institutional_holders
        
        # جلب الأرباح
        earnings = ticker.earnings
        dividends = ticker.dividends
        
        return {
            "info": info,
            "history": hist,
            "financials": financials,
            "balance_sheet": balance_sheet,
            "cashflow": cashflow,
            "major_holders": major_holders,
            "institutional_holders": institutional_holders,
            "earnings": earnings,
            "dividends": dividends,
            "recommendations": ticker.recommendations,
            "news": ticker.news[:5] if hasattr(ticker, 'news') else []
        }
    except Exception as e:
        st.error(f"❌ خطأ في جلب البيانات: {str(e)}")
        return None

# وظيفة لحساب المؤشرات الفنية
def calculate_technical_indicators(data):
    """حساب المؤشرات الفنية"""
    indicators = {}
    
    if data is not None and not data.empty:
        close = data['Close']
        
        # المتوسطات المتحركة
        indicators['SMA_20'] = close.rolling(window=20).mean()
        indicators['SMA_50'] = close.rolling(window=50).mean()
        indicators['SMA_200'] = close.rolling(window=200).mean()
        
        # بولينجر باندز
        indicators['BB_middle'] = close.rolling(window=20).mean()
        bb_std = close.rolling(window=20).std()
        indicators['BB_upper'] = indicators['BB_middle'] + (bb_std * 2)
        indicators['BB_lower'] = indicators['BB_middle'] - (bb_std * 2)
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        indicators['MACD'] = exp1 - exp2
        indicators['Signal'] = indicators['MACD'].ewm(span=9, adjust=False).mean()
        indicators['MACD_hist'] = indicators['MACD'] - indicators['Signal']
    
    return indicators

# إنشاء رسم بياني متقدم باستخدام Plotly
def create_candlestick_chart(data, indicators=None):
    """إنشاء رسم بياني شموع مع مؤشرات"""
    if data is None or data.empty:
        return None
    
    fig = go.Figure()
    
    # إضافة شموع
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='شموع يابانية',
        increasing_line_color='#00cc00',
        decreasing_line_color='#ff3333'
    ))
    
    # إضافة المتوسطات المتحركة
    if indicators:
        if 'SMA_20' in indicators and not indicators['SMA_20'].isna().all():
            fig.add_trace(go.Scatter(
                x=data.index,
                y=indicators['SMA_20'],
                name='SMA 20',
                line=dict(color='orange', width=1.5)
            ))
        
        if 'SMA_50' in indicators and not indicators['SMA_50'].isna().all():
            fig.add_trace(go.Scatter(
                x=data.index,
                y=indicators['SMA_50'],
                name='SMA 50',
                line=dict(color='blue', width=1.5)
            ))
        
        if 'BB_upper' in indicators and not indicators['BB_upper'].isna().all():
            fig.add_trace(go.Scatter(
                x=data.index,
                y=indicators['BB_upper'],
                name='BB Upper',
                line=dict(color='gray', width=1, dash='dash')
            ))
            fig.add_trace(go.Scatter(
                x=data.index,
                y=indicators['BB_lower'],
                name='BB Lower',
                line=dict(color='gray', width=1, dash='dash'),
                fill='tonexty',
                fillcolor='rgba(128, 128, 128, 0.1)'
            ))
    
    # تنسيق الرسم
    fig.update_layout(
        title='📈 رسم بياني متقدم',
        xaxis_title='التاريخ',
        yaxis_title='السعر ($)',
        template='plotly_dark',
        height=600,
        xaxis_rangeslider_visible=False,
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

# الواجهة الرئيسية
st.markdown('<div class="main-header">🇺🇸 منصة تحليل الأسهم الأمريكية</div>', unsafe_allow_html=True)

# قسم البحث والاختيار
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    # جلب قائمة الأسهم
    stocks_df = get_us_stocks()
    
    # إنشاء خيارات للاختيار مع إمكانية البحث
    stock_options = {f"{row['symbol']} - {row['name']}": row['symbol'] 
                    for _, row in stocks_df.iterrows()}
    
    # إضافة خيار للبحث المخصص
    all_options = list(stock_options.keys())
    all_options.append("🔍 بحث مخصص (أدخل رمز السهم)")
    
    selected_display = st.selectbox(
        "🔍 اختر أو ابحث عن السهم:",
        options=all_options,
        index=0,
        help="ابحث عن السهم الذي تريده أو اختر من القائمة"
    )
    
    if selected_display == "🔍 بحث مخصص (أدخل رمز السهم)":
        selected_symbol = st.text_input(
            "📝 أدخل رمز السهم:",
            value="AAPL",
            help="مثال: AAPL, MSFT, GOOGL"
        ).upper()
    else:
        selected_symbol = stock_options[selected_display]

with col2:
    # اختيار الفترة الزمنية
    period_options = {
        "يوم": "1d",
        "5 أيام": "5d",
        "شهر": "1mo",
        "3 أشهر": "3mo",
        "6 أشهر": "6mo",
        "سنة": "1y",
        "سنتين": "2y",
        "5 سنوات": "5y",
        "الكل": "max"
    }
    selected_period = st.selectbox("📅 الفترة:", list(period_options.keys()), index=5)

with col3:
    # زر التحديث
    if st.button("🔄 تحديث", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# جلب وعرض البيانات
if selected_symbol:
    with st.spinner(f"🔄 جاري تحميل بيانات {selected_symbol}..."):
        stock_data = fetch_stock_data(selected_symbol, period_options[selected_period])
        
        if stock_data:
            info = stock_data["info"]
            history = stock_data["history"]
            
            # عرض معلومات أساسية
            st.divider()
            
            # بطاقات المعلومات الرئيسية
            col1, col2, col3, col4, col5 = st.columns(5)
            
            current_price = info.get('regularMarketPrice', info.get('currentPrice', 0))
            previous_close = info.get('regularMarketPreviousClose', info.get('previousClose', 0))
            
            with col1:
                change = current_price - previous_close if current_price and previous_close else 0
                change_percent = (change / previous_close * 100) if previous_close else 0
                delta_color = "🟢" if change >= 0 else "🔴"
                st.metric(
                    label="💰 السعر الحالي",
                    value=f"${current_price:.2f}" if current_price else "N/A",
                    delta=f"{change:+.2f} ({change_percent:+.2f}%)",
                    delta_color="normal"
                )
            
            with col2:
                st.metric(
                    label="📊 القيمة السوقية",
                    value=f"${info.get('marketCap', 0) / 1e9:.2f}B" if info.get('marketCap') else "N/A"
                )
            
            with col3:
                pe = info.get('trailingPE', 0)
                st.metric(
                    label="📈 مكرر الأرباح (P/E)",
                    value=f"{pe:.2f}" if pe else "N/A"
                )
            
            with col4:
                eps = info.get('trailingEps', 0)
                st.metric(
                    label="💵 ربحية السهم (EPS)",
                    value=f"${eps:.2f}" if eps else "N/A"
                )
            
            with col5:
                dividend = info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
                st.metric(
                    label="💸 عائد التوزيعات",
                    value=f"{dividend:.2f}%" if dividend else "N/A"
                )
            
            # معلومات إضافية
            st.divider()
            
            # الأقسام الرئيسية
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📈 الرسوم البيانية",
                "🏛️ القوائم المالية", 
                "📊 المؤشرات المالية",
                "👥 الملكية والتحليلات",
                "📰 الأخبار والتوصيات"
            ])
            
            with tab1:
                if not history.empty:
                    # حساب المؤشرات الفنية
                    indicators = calculate_technical_indicators(history)
                    
                    # اختيار نوع الرسم البياني
                    chart_type = st.radio(
                        "نوع الرسم البياني:",
                        ["شموع يابانية", "خطي", "مساحي"],
                        horizontal=True
                    )
                    
                    # عرض الرسوم البيانية
                    if chart_type == "شموع يابانية":
                        fig = create_candlestick_chart(history, indicators)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                    elif chart_type == "خطي":
                        st.line_chart(history['Close'])
                    else:
                        st.area_chart(history['Close'])
                    
                    # المؤشرات الفنية الإضافية
                    st.subheader("📊 المؤشرات الفنية")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if 'RSI' in indicators and not indicators['RSI'].isna().all():
                            rsi_value = indicators['RSI'].iloc[-1]
                            st.metric(
                                label="RSI (مؤشر القوة النسبية)",
                                value=f"{rsi_value:.2f}",
                                delta="تشبع شراء" if rsi_value > 70 else "تشبع بيع" if rsi_value < 30 else "محايد"
                            )
                    
                    with col2:
                        if 'MACD' in indicators and 'Signal' in indicators:
                            macd_value = indicators['MACD'].iloc[-1]
                            signal_value = indicators['Signal'].iloc[-1]
                            st.metric(
                                label="MACD",
                                value=f"{macd_value:.4f}",
                                delta=f"Signal: {signal_value:.4f}"
                            )
                    
                    with col3:
                        volume = history['Volume'].iloc[-1] if not history.empty else 0
                        avg_volume = history['Volume'].mean() if not history.empty else 0
                        st.metric(
                            label="حجم التداول",
                            value=f"{volume:,.0f}",
                            delta=f"{((volume/avg_volume - 1) * 100):.1f}%" if avg_volume > 0 else "0%"
                        )
                    
                    # عرض بيانات الجدول
                    with st.expander("📋 عرض بيانات السعر"):
                        st.dataframe(
                            history.tail(20).style.format({
                                'Open': '${:.2f}',
                                'High': '${:.2f}',
                                'Low': '${:.2f}',
                                'Close': '${:.2f}',
                                'Volume': '{:,.0f}'
                            }),
                            use_container_width=True
                        )
                else:
                    st.warning("⚠️ لا توجد بيانات تاريخية متاحة")
            
            with tab2:
                st.subheader("🏛️ القوائم المالية")
                
                # عرض القوائم المالية
                financials = stock_data.get("financials")
                balance = stock_data.get("balance_sheet")
                cashflow = stock_data.get("cashflow")
                
                if financials is not None and not financials.empty:
                    with st.expander("📊 قائمة الدخل", expanded=True):
                        st.dataframe(financials, use_container_width=True)
                else:
                    st.info("📝 قائمة الدخل غير متوفرة")
                
                if balance is not None and not balance.empty:
                    with st.expander("📊 الميزانية العمومية"):
                        st.dataframe(balance, use_container_width=True)
                else:
                    st.info("📝 الميزانية العمومية غير متوفرة")
                
                if cashflow is not None and not cashflow.empty:
                    with st.expander("📊 قائمة التدفقات النقدية"):
                        st.dataframe(cashflow, use_container_width=True)
                else:
                    st.info("📝 قائمة التدفقات النقدية غير متوفرة")
            
            with tab3:
                st.subheader("📊 المؤشرات المالية الرئيسية")
                
                # جمع المؤشرات المالية
                metrics = {
                    "الربحية": {
                        "هامش الربح": info.get('profitMargins', 0) * 100 if info.get('profitMargins') else None,
                        "العائد على حقوق الملكية (ROE)": info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else None,
                        "العائد على الأصول (ROA)": info.get('returnOnAssets', 0) * 100 if info.get('returnOnAssets') else None,
                    },
                    "السيولة": {
                        "النسبة الحالية": info.get('currentRatio', None),
                        "النسبة السريعة": info.get('quickRatio', None),
                    },
                    "الديون": {
                        "نسبة الدين إلى حقوق الملكية": info.get('debtToEquity', None),
                        "الدين الإجمالي": info.get('totalDebt', None),
                    },
                    "النمو": {
                        "نمو الأرباح": info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else None,
                        "نمو الإيرادات": info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else None,
                    }
                }
                
                # عرض المؤشرات
                for category, values in metrics.items():
                    st.write(f"**{category}**")
                    cols = st.columns(len(values))
                    for idx, (key, value) in enumerate(values.items()):
                        with cols[idx]:
                            if value is not None:
                                if isinstance(value, float):
                                    st.metric(
                                        label=key,
                                        value=f"{value:.2f}%" if key in ["هامش الربح", "العائد على حقوق الملكية", "العائد على الأصول", "نمو الأرباح", "نمو الإيرادات"] else f"{value:.2f}"
                                    )
                                else:
                                    st.metric(label=key, value=f"${value:,.0f}" if isinstance(value, (int, float)) and value > 1000 else str(value))
                            else:
                                st.metric(label=key, value="N/A")
                    st.divider()
                
                # مقارنة مع القطاع
                st.subheader("📊 مقارنة مع متوسط القطاع")
                sector = info.get('sector', 'Technology')
                
                # بيانات وهمية للمقارنة (يمكن استبدالها ببيانات حقيقية)
                sector_data = {
                    "Technology": {"pe": 25.5, "roe": 15.2, "margin": 12.8},
                    "Healthcare": {"pe": 22.3, "roe": 18.5, "margin": 10.2},
                    "Financial": {"pe": 15.8, "roe": 12.1, "margin": 8.5},
                    "Consumer": {"pe": 20.1, "roe": 14.7, "margin": 9.8},
                }
                
                if sector in sector_data:
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric(
                            "مكرر الأرباح (P/E)",
                            f"{info.get('trailingPE', 0):.2f}",
                            delta=f"{info.get('trailingPE', 0) - sector_data[sector]['pe']:.2f}"
                        )
                    with cols[1]:
                        st.metric(
                            "العائد على حقوق الملكية",
                            f"{info.get('returnOnEquity', 0) * 100:.2f}%",
                            delta=f"{(info.get('returnOnEquity', 0) * 100 - sector_data[sector]['roe']):.2f}%"
                        )
                    with cols[2]:
                        st.metric(
                            "هامش الربح",
                            f"{info.get('profitMargins', 0) * 100:.2f}%",
                            delta=f"{(info.get('profitMargins', 0) * 100 - sector_data[sector]['margin']):.2f}%"
                        )
            
            with tab4:
                st.subheader("👥 الملكية والتحليلات")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # عرض كبار المالكين
                    major_holders = stock_data.get("major_holders")
                    if major_holders is not None and not major_holders.empty:
                        st.write("**🏢 كبار المالكين**")
                        st.dataframe(major_holders, use_container_width=True)
                    else:
                        st.info("📝 بيانات كبار المالكين غير متوفرة")
                
                with col2:
                    # عرض المؤسسات المالكة
                    institutional = stock_data.get("institutional_holders")
                    if institutional is not None and not institutional.empty:
                        st.write("**🏛️ المالكين المؤسسيين**")
                        st.dataframe(institutional.head(10), use_container_width=True)
                    else:
                        st.info("📝 بيانات المالكين المؤسسيين غير متوفرة")
                
                # عرض بيانات الأرباح
                st.divider()
                earnings = stock_data.get("earnings")
                if earnings is not None and not earnings.empty:
                    st.subheader("💹 بيانات الأرباح")
                    st.dataframe(earnings, use_container_width=True)
                else:
                    st.info("📝 بيانات الأرباح غير متوفرة")
                
                # عرض التوزيعات
                dividends = stock_data.get("dividends")
                if dividends is not None and not dividends.empty:
                    st.subheader("💰 توزيعات الأرباح")
                    st.line_chart(dividends)
                else:
                    st.info("📝 بيانات التوزيعات غير متوفرة")
            
            with tab5:
                st.subheader("📰 الأخبار والتوصيات")
                
                # عرض التوصيات
                recommendations = stock_data.get("recommendations")
                if recommendations is not None and not recommendations.empty:
                    st.write("**📊 توصيات المحللين**")
                    st.dataframe(recommendations, use_container_width=True)
                    
                    # رسم بياني للتوصيات
                    if 'Grade' in recommendations.columns:
                        grade_counts = recommendations['Grade'].value_counts()
                        fig = px.pie(
                            values=grade_counts.values,
                            names=grade_counts.index,
                            title="توزيع توصيات المحللين"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("📝 لا توجد توصيات متاحة حالياً")
                
                # عرض الأخبار
                st.divider()
                news = stock_data.get("news", [])
                if news:
                    st.write("**📰 آخر الأخبار**")
                    for article in news[:5]:
                        with st.expander(f"📌 {article.get('title', 'خبر')[:80]}..."):
                            if 'description' in article:
                                st.write(f"📝 {article.get('description', 'لا يوجد وصف')}")
                            if 'publisher' in article:
                                st.caption(f"🏢 المصدر: {article.get('publisher', 'غير معروف')}")
                            if 'link' in article:
                                st.markdown(f"[🔗 قراءة المزيد]({article.get('link', '#')})")
                else:
                    st.info("📝 لا توجد أخبار متاحة حالياً")
            
            # إضافة معلومات إضافية في الشريط الجانبي
            with st.sidebar:
                st.image("https://img.icons8.com/color/96/000000/line-chart.png", width=80)
                st.title("📊 ByToBy-Pro4")
                st.caption("منصة تحليل الأسهم الأمريكية")
                st.divider()
                
                st.subheader("ℹ️ معلومات السهم")
                st.write(f"**🏢 الشركة:** {info.get('longName', 'غير معروف')}")
                st.write(f"**🌍 القطاع:** {info.get('sector', 'غير معروف')}")
                st.write(f"**🌐 الصناعة:** {info.get('industry', 'غير معروف')}")
                st.write(f"**📍 المقر:** {info.get('country', 'غير معروف')}")
                st.write(f"**👥 الموظفين:** {info.get('fullTimeEmployees', 'غير معروف'):,}" if info.get('fullTimeEmployees') else "N/A")
                st.write(f"**📅 التحديث:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                
                st.divider()
                
                with st.expander("⚙️ الإعدادات"):
                    show_indicators = st.checkbox("📊 إظهار المؤشرات", value=True)
                    show_volume = st.checkbox("📈 إظهار حجم التداول", value=True)
                    auto_refresh = st.checkbox("🔄 تحديث تلقائي", value=False)
                    if auto_refresh:
                        st.slider("معدل التحديث (دقائق)", 1, 30, 5)
                
                st.divider()
                st.caption("© 2026 ByToBy-Pro4 | جميع الحقوق محفوظة")
                st.caption("📊 البيانات مقدمة من Yahoo Finance")
                
        else:
            st.error(f"❌ تعذر جلب بيانات السهم {selected_symbol}. تأكد من صحة رمز السهم.")
else:
    st.info("👈 اختر أو ابحث عن سهم من القائمة الجانبية للبدء")
