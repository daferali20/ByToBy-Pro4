import streamlit as st
import sys
import os
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# إعداد الصفحة
st.set_page_config(
    page_title="🔍 الماسح الذكي للأسهم الأمريكية",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تحميل CSS مخصص
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 20px;
    }
    .scan-result {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 5px;
    }
    .signal-bullish {
        color: #00cc00;
        font-weight: bold;
    }
    .signal-bearish {
        color: #ff3333;
        font-weight: bold;
    }
    .signal-neutral {
        color: #ffa500;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============= فئات وأدوات الماسح الذكي =============

class SmartScanner:
    """ماسح ذكي للأسهم مع تحليل فني وأساسي"""
    
    def __init__(self, watchlist=None):
        self.watchlist = watchlist or []
        self.results = []
        
    def calculate_indicators(self, data):
        """حساب المؤشرات الفنية"""
        if data is None or data.empty:
            return None
        
        close = data['Close']
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # المتوسطات المتحركة
        sma_20 = close.rolling(window=20).mean()
        sma_50 = close.rolling(window=50).mean()
        sma_200 = close.rolling(window=200).mean()
        
        # MACD
        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        macd_hist = macd - signal
        
        # حجم التداول
        avg_volume = data['Volume'].rolling(window=20).mean()
        volume_ratio = data['Volume'] / avg_volume
        
        # بولينجر باندز
        bb_middle = close.rolling(window=20).mean()
        bb_std = close.rolling(window=20).std()
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)
        
        return {
            'rsi': rsi,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'sma_200': sma_200,
            'macd': macd,
            'signal': signal,
            'macd_hist': macd_hist,
            'volume_ratio': volume_ratio,
            'bb_upper': bb_upper,
            'bb_lower': bb_lower,
            'bb_middle': bb_middle
        }
    
    def analyze_stock(self, symbol):
        """تحليل سهم فردي"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # جلب البيانات التاريخية
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                return None
            
            # حساب المؤشرات
            indicators = self.calculate_indicators(hist)
            if indicators is None:
                return None
            
            # استخراج القيم الأخيرة
            latest = hist.iloc[-1]
            close = latest['Close']
            volume = latest['Volume']
            
            # تحليل المؤشرات
            rsi = indicators['rsi'].iloc[-1] if not pd.isna(indicators['rsi'].iloc[-1]) else 50
            sma_20 = indicators['sma_20'].iloc[-1] if not pd.isna(indicators['sma_20'].iloc[-1]) else close
            sma_50 = indicators['sma_50'].iloc[-1] if not pd.isna(indicators['sma_50'].iloc[-1]) else close
            sma_200 = indicators['sma_200'].iloc[-1] if not pd.isna(indicators['sma_200'].iloc[-1]) else close
            macd = indicators['macd'].iloc[-1] if not pd.isna(indicators['macd'].iloc[-1]) else 0
            signal = indicators['signal'].iloc[-1] if not pd.isna(indicators['signal'].iloc[-1]) else 0
            volume_ratio = indicators['volume_ratio'].iloc[-1] if not pd.isna(indicators['volume_ratio'].iloc[-1]) else 1
            
            # تحديد الاتجاه
            trend = "محايد"
            if close > sma_20 > sma_50:
                trend = "صاعد قوي"
            elif close > sma_20 and close > sma_50:
                trend = "صاعد"
            elif close < sma_20 < sma_50:
                trend = "هابط قوي"
            elif close < sma_20 and close < sma_50:
                trend = "هابط"
            
            # إشارة MACD
            macd_signal = "محايد"
            if macd > signal and macd > 0:
                macd_signal = "شراء"
            elif macd < signal and macd < 0:
                macd_signal = "بيع"
            
            # حساب نقاط القوة
            score = 0
            if rsi < 30:
                score += 2  # تشبع بيع (فرصة شراء)
            elif rsi > 70:
                score -= 2  # تشبع شراء
            else:
                score += 1
            
            if close > sma_20:
                score += 1
            if close > sma_50:
                score += 1
            if close > sma_200:
                score += 1
            if macd > signal:
                score += 1
            if volume_ratio > 1.5:
                score += 1
            
            # تحديد التوصية
            if score >= 5:
                recommendation = "شراء قوي 🔥"
            elif score >= 3:
                recommendation = "شراء 📈"
            elif score >= 1:
                recommendation = "احتفاظ ⚖️"
            elif score >= -1:
                recommendation = "بيع جزئي 📉"
            else:
                recommendation = "بيع قوي 🚨"
            
            # جمع البيانات الأساسية
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'غير محدد'),
                'close': close,
                'change_1d': ((close - hist.iloc[-2]['Close']) / hist.iloc[-2]['Close'] * 100) if len(hist) > 1 else 0,
                'volume': volume,
                'volume_ratio': volume_ratio,
                'rsi': rsi,
                'macd_signal': macd_signal,
                'trend': trend,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'sma_200': sma_200,
                'score': score,
                'recommendation': recommendation,
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
            }
            
        except Exception as e:
            return None
    
    def scan_market(self, min_rsi=0, max_rsi=100, trend_filter="الكل", min_volume=0, max_stocks=None, sort_by="score"):
        """مسح السوق مع خيارات التصفية"""
        results = []
        
        # تحديد الأسهم المراد مسحها
        symbols = self.watchlist[:max_stocks] if max_stocks else self.watchlist
        
        # استخدام المعالجة المتوازية لتسريع المسح
        with st.spinner("🔄 جاري مسح الأسهم..."):
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_symbol = {executor.submit(self.analyze_stock, symbol): symbol for symbol in symbols}
                
                for future in as_completed(future_to_symbol):
                    result = future.result()
                    if result:
                        results.append(result)
        
        # تطبيق الفلاتر
        filtered_results = []
        for result in results:
            # فلتر RSI
            if not (min_rsi <= result['rsi'] <= max_rsi):
                continue
            
            # فلتر الاتجاه
            if trend_filter != "الكل":
                if trend_filter == "صاعد" and result['trend'] not in ["صاعد", "صاعد قوي"]:
                    continue
                elif trend_filter == "هابط" and result['trend'] not in ["هابط", "هابط قوي"]:
                    continue
            
            # فلتر الحجم
            if result['volume_ratio'] < min_volume:
                continue
            
            filtered_results.append(result)
        
        # ترتيب النتائج
        if sort_by == "score":
            filtered_results.sort(key=lambda x: x['score'], reverse=True)
        elif sort_by == "rsi":
            filtered_results.sort(key=lambda x: x['rsi'])
        elif sort_by == "change":
            filtered_results.sort(key=lambda x: x['change_1d'], reverse=True)
        elif sort_by == "volume":
            filtered_results.sort(key=lambda x: x['volume_ratio'], reverse=True)
        
        return filtered_results

# ============= قائمة الأسهم الأمريكية =============

def get_us_watchlist():
    """قائمة الأسهم الأمريكية للمسح"""
    return [
        # التكنولوجيا
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", 
        "ADBE", "CRM", "AMD", "INTC", "ORCL", "IBM", "CSCO",
        "QCOM", "TXN", "AVGO", "NOW", "INTU", "SHOP", "SNOW",
        
        # المالية
        "JPM", "BAC", "WFC", "GS", "MS", "V", "MA", "PYPL", "SQ",
        
        # الرعاية الصحية
        "JNJ", "UNH", "PFE", "TMO", "ABT", "LLY", "MRK", "ABBV",
        "CVS", "BMY", "AMGN", "GILD", "REGN", "VRTX",
        
        # المستهلك
        "WMT", "COST", "PG", "KO", "PEP", "MCD", "SBUX", "NKE",
        "HD", "LOW", "TGT", "DIS", "NFLX", "T", "VZ",
        
        # الطاقة والصناعة
        "XOM", "CVX", "BA", "GE", "CAT", "DE", "HON", "RTX",
        
        # أخرى
        "SPY", "QQQ", "DIA", "IWM", "GLD", "SLV", "USO"
    ]

# ============= الواجهة الرئيسية =============

st.markdown('<div class="main-header">🔍 الماسح الذكي للأسهم الأمريكية</div>', unsafe_allow_html=True)

# أقسام الواجهة
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.info("🔎 ابحث عن فرص استثمارية باستخدام المؤشرات الفنية المتقدمة")
    
    # اختيار الأسهم
    stock_list_option = st.radio(
        "قائمة الأسهم:",
        ["القائمة الكاملة (70+ سهم)", "قائمة مخصصة"],
        horizontal=True
    )
    
    if stock_list_option == "القائمة الكاملة (70+ سهم)":
        watchlist = get_us_watchlist()
    else:
        custom_stocks = st.text_input(
            "أدخل رموز الأسهم (افصلها بفواصل):",
            value="AAPL, MSFT, NVDA, TSLA"
        )
        watchlist = [s.strip().upper() for s in custom_stocks.split(',') if s.strip()]

with col2:
    # فلاتر المسح
    st.subheader("⚙️ فلاتر المسح")
    
    rsi_range = st.slider(
        "مؤشر القوة النسبية (RSI)",
        0, 100, (30, 70),
        help="القيم الأقل من 30 تشير إلى تشبع بيع، والأعلى من 70 تشير إلى تشبع شراء"
    )
    
    trend_filter = st.selectbox(
        "الاتجاه",
        ["الكل", "صاعد", "صاعد قوي", "هابط", "هابط قوي"],
        index=0
    )

with col3:
    st.subheader("📊 إعدادات إضافية")
    
    min_volume_ratio = st.slider(
        "نسبة الحجم الأدنى",
        0.0, 5.0, 1.0, 0.1,
        help="نسبة حجم التداول الحالي إلى متوسط 20 يوم"
    )
    
    sort_by = st.selectbox(
        "ترتيب النتائج حسب:",
        ["النقاط (الأعلى أولاً)", "RSI (الأقل أولاً)", "التغير اليومي", "نسبة الحجم"],
        index=0
    )
    
    max_results = st.slider(
        "الحد الأقصى للنتائج",
        10, 100, 50, 10
    )

# زر البدء
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    start_scan = st.button(
        "🚀 بدء المسح الذكي",
        use_container_width=True,
        type="primary"
    )

# تنفيذ المسح
if start_scan:
    if not watchlist:
        st.warning("⚠️ الرجاء اختيار أو إدخال رموز الأسهم")
    else:
        st.divider()
        
        # إنشاء الماسح
        scanner = SmartScanner(watchlist)
        
        # تنفيذ المسح
        with st.spinner(f"🔄 جاري مسح {len(watchlist)} سهماً..."):
            results = scanner.scan_market(
                min_rsi=rsi_range[0],
                max_rsi=rsi_range[1],
                trend_filter=trend_filter,
                min_volume=min_volume_ratio,
                max_stocks=max_results,
                sort_by="score" if sort_by == "النقاط (الأعلى أولاً)" else 
                        "rsi" if sort_by == "RSI (الأقل أولاً)" else
                        "change" if sort_by == "التغير اليومي" else "volume"
            )
        
        # عرض النتائج
        if results:
            # عرض الإحصائيات السريعة
            st.markdown(f"### 📊 نتائج المسح - تم العثور على {len(results)} سهماً مطابقاً")
            
            # إحصائيات سريعة
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "✅ إجمالي النتائج",
                    len(results),
                    delta=f"{len(results)} سهم"
                )
            with col2:
                avg_score = sum(r['score'] for r in results) / len(results) if results else 0
                st.metric(
                    "⭐ متوسط النقاط",
                    f"{avg_score:.1f}"
                )
            with col3:
                buy_signals = sum(1 for r in results if "شراء" in r['recommendation'])
                st.metric(
                    "📈 إشارات شراء",
                    buy_signals,
                    delta=f"{buy_signals/len(results)*100:.0f}%"
                )
            with col4:
                avg_rsi = sum(r['rsi'] for r in results) / len(results) if results else 0
                st.metric(
                    "📊 متوسط RSI",
                    f"{avg_rsi:.1f}"
                )
            
            # تحويل النتائج إلى DataFrame
            df_results = pd.DataFrame(results)
            
            # تنسيق الأعمدة
            display_columns = {
                'symbol': 'الرمز',
                'name': 'الاسم',
                'sector': 'القطاع',
                'close': 'السعر ($)',
                'change_1d': 'التغير %',
                'volume_ratio': 'نسبة الحجم',
                'rsi': 'RSI',
                'trend': 'الاتجاه',
                'macd_signal': 'إشارة MACD',
                'recommendation': 'التوصية',
                'score': 'النقاط'
            }
            
            df_display = df_results[list(display_columns.keys())].copy()
            df_display = df_display.rename(columns=display_columns)
            
            # تنسيق الأرقام
            df_display['السعر ($)'] = df_display['السعر ($)'].map('${:,.2f}'.format)
            df_display['التغير %'] = df_display['التغير %'].map('{:+.2f}%'.format)
            df_display['نسبة الحجم'] = df_display['نسبة الحجم'].map('{:.2f}x'.format)
            df_display['RSI'] = df_display['RSI'].map('{:.1f}'.format)
            df_display['النقاط'] = df_display['النقاط'].map('{:.0f}'.format)
            
            # عرض الجدول
            st.dataframe(
                df_display,
                use_container_width=True,
                height=400,
                column_config={
                    "الرمز": st.column_config.TextColumn("الرمز", width="small"),
                    "الاسم": st.column_config.TextColumn("الاسم", width="medium"),
                    "القطاع": st.column_config.TextColumn("القطاع", width="medium"),
                    "السعر ($)": st.column_config.TextColumn("السعر ($)", width="small"),
                    "التغير %": st.column_config.TextColumn("التغير %", width="small"),
                    "نسبة الحجم": st.column_config.TextColumn("نسبة الحجم", width="small"),
                    "RSI": st.column_config.TextColumn("RSI", width="small"),
                    "الاتجاه": st.column_config.TextColumn("الاتجاه", width="small"),
                    "إشارة MACD": st.column_config.TextColumn("إشارة MACD", width="small"),
                    "التوصية": st.column_config.TextColumn("التوصية", width="medium"),
                    "النقاط": st.column_config.TextColumn("النقاط", width="small"),
                }
            )
            
            # عرض تفاصيل الأسهم المختارة
            st.divider()
            st.subheader("📈 تفاصيل الأسهم المختارة")
            
            selected_stocks = st.multiselect(
                "اختر الأسهم لعرض تفاصيلها:",
                options=df_results['symbol'].tolist(),
                default=df_results['symbol'].tolist()[:3]
            )
            
            if selected_stocks:
                for symbol in selected_stocks:
                    stock_data = df_results[df_results['symbol'] == symbol].iloc[0]
                    
                    with st.expander(f"📊 {symbol} - {stock_data['name']} ({stock_data['sector']})"):
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric(
                                "السعر الحالي",
                                f"${stock_data['close']:.2f}",
                                delta=f"{stock_data['change_1d']:.2f}%"
                            )
                        with col2:
                            st.metric(
                                "RSI",
                                f"{stock_data['rsi']:.1f}",
                                delta="تشبع بيع" if stock_data['rsi'] < 30 else "تشبع شراء" if stock_data['rsi'] > 70 else "محايد"
                            )
                        with col3:
                            st.metric(
                                "المتوسطات",
                                f"SMA20: ${stock_data['sma_20']:.2f}",
                                delta=f"SMA50: ${stock_data['sma_50']:.2f}"
                            )
                        with col4:
                            st.metric(
                                "التوصية",
                                stock_data['recommendation'],
                                delta=f"النقاط: {stock_data['score']}"
                            )
                        
                        # عرض معلومات إضافية
                        st.write(f"""
                        - 📊 **الاتجاه**: {stock_data['trend']}
                        - 📈 **إشارة MACD**: {stock_data['macd_signal']}
                        - 💰 **القيمة السوقية**: ${stock_data['market_cap']/1e9:.2f}B
                        - 📊 **نسبة التداول**: {stock_data['volume_ratio']:.2f}x
                        """)
                        
                        # رسم بياني سريع للسهم
                        try:
                            ticker = yf.Ticker(symbol)
                            hist = ticker.history(period="3mo")
                            if not hist.empty:
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(
                                    x=hist.index,
                                    y=hist['Close'],
                                    mode='lines',
                                    name='السعر',
                                    line=dict(color='#1f77b4', width=2)
                                ))
                                fig.update_layout(
                                    title=f"أداء {symbol} - آخر 3 أشهر",
                                    xaxis_title="التاريخ",
                                    yaxis_title="السعر ($)",
                                    height=300,
                                    template='plotly_dark',
                                    showlegend=False
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        except:
                            pass
            else:
                st.info("👆 اختر أسهم لعرض التفاصيل")
            
            # تصدير النتائج
            st.divider()
            col1, col2, col3 = st.columns(3)
            with col1:
                csv = df_display.to_csv(index=False)
                st.download_button(
                    label="📥 تحميل النتائج CSV",
                    data=csv,
                    file_name=f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                if st.button("📊 عرض التوزيعات", use_container_width=True):
                    # عرض إحصائيات إضافية
                    st.subheader("📊 توزيع النتائج")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        # توزيع RSI
                        fig1 = px.histogram(
                            df_results,
                            x='rsi',
                            title='توزيع RSI',
                            labels={'rsi': 'RSI', 'count': 'العدد'},
                            color_discrete_sequence=['#667eea']
                        )
                        fig1.add_vline(x=30, line_dash="dash", line_color="green")
                        fig1.add_vline(x=70, line_dash="dash", line_color="red")
                        st.plotly_chart(fig1, use_container_width=True)
                    
                    with col2:
                        # توزيع التوصيات
                        recommendations_count = df_results['recommendation'].value_counts()
                        fig2 = px.pie(
                            values=recommendations_count.values,
                            names=recommendations_count.index,
                            title='توزيع التوصيات',
                            color_discrete_sequence=px.colors.qualitative.Set3
                        )
                        st.plotly_chart(fig2, use_container_width=True)
            
            with col3:
                if st.button("📈 أفضل 10 أسهم", use_container_width=True):
                    top_10 = df_results.nlargest(10, 'score')[['symbol', 'name', 'score', 'recommendation']]
                    st.dataframe(top_10, use_container_width=True)
            
        else:
            st.warning("❌ لا توجد أسهم تطابق الشروط المحددة. حاول تعديل الفلاتر.")
else:
    st.info("👈 اضغط على زر 'بدء المسح الذكي' لبدء عملية المسح")

# معلومات إضافية في الشريط الجانبي
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/line-chart.png", width=80)
    st.title("🔍 الماسح الذكي")
    st.caption("منصة متقدمة لمسح الأسهم الأمريكية")
    st.divider()
    
    st.subheader("ℹ️ عن الماسح")
    st.write("""
    📊 **المؤشرات المستخدمة:**
    - RSI (مؤشر القوة النسبية)
    - المتوسطات المتحركة (SMA 20, 50, 200)
    - MACD
    - حجم التداول
    - بولينجر باندز
    
    🎯 **نظام النقاط:**
    - RSI < 30: +2 نقطة
    - السعر فوق SMA20: +1 نقطة
    - السعر فوق SMA50: +1 نقطة
    - السعر فوق SMA200: +1 نقطة
    - MACD فوق الإشارة: +1 نقطة
    - حجم التداول > 1.5x: +1 نقطة
    """)
    
    st.divider()
    
    with st.expander("📝 نصائح للاستخدام"):
        st.markdown("""
        💡 **نصائح:**
        1. استخدم RSI 30-70 للبحث عن أسهم متوازنة
        2. حجم التداول العالي يشير إلى اهتمام كبير
        3. ابحث عن الأسهم ذات النقاط العالية (5+)
        4. اجمع بين التحليل الفني والأساسي
        5. استخدم التوصيات كأداة مساعدة وليس قراراً نهائياً
        """)
    
    st.divider()
    st.caption("© 2026 ByToBy-Pro4 | جميع الحقوق محفوظة")
    st.caption("📊 البيانات مقدمة من Yahoo Finance")
