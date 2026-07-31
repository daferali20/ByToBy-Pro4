# pages/8_ai_insights.py

import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf

# إعداد المسار
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st

# ============= الفئات المحسنة =============

class USMarketDataProvider:
    """مزود بيانات السوق الأمريكية"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.ticker = yf.Ticker(symbol)
        
    def get_history(self, period: str = "6mo") -> pd.DataFrame:
        """جلب البيانات التاريخية"""
        try:
            hist = self.ticker.history(period=period)
            return hist
        except Exception as e:
            st.error(f"خطأ في جلب البيانات: {str(e)}")
            return pd.DataFrame()
    
    def get_info(self) -> dict:
        """جلب معلومات السهم"""
        try:
            return self.ticker.info
        except:
            return {}

class TechnicalAnalyzer:
    """محلل فني متقدم"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.indicators = {}
        
    def calculate_all_indicators(self) -> dict:
        """حساب جميع المؤشرات الفنية"""
        if self.df.empty:
            return {}
        
        close = self.df['Close']
        high = self.df['High']
        low = self.df['Low']
        volume = self.df['Volume']
        
        # 1. المتوسطات المتحركة
        self.indicators['SMA_5'] = close.rolling(5).mean()
        self.indicators['SMA_10'] = close.rolling(10).mean()
        self.indicators['SMA_20'] = close.rolling(20).mean()
        self.indicators['SMA_50'] = close.rolling(50).mean()
        self.indicators['SMA_100'] = close.rolling(100).mean()
        self.indicators['SMA_200'] = close.rolling(200).mean()
        
        # 2. RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        self.indicators['RSI'] = 100 - (100 / (1 + rs))
        
        # 3. MACD
        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        self.indicators['MACD'] = exp1 - exp2
        self.indicators['Signal'] = self.indicators['MACD'].ewm(span=9, adjust=False).mean()
        self.indicators['MACD_Hist'] = self.indicators['MACD'] - self.indicators['Signal']
        
        # 4. بولينجر باندز
        bb_middle = close.rolling(20).mean()
        bb_std = close.rolling(20).std()
        self.indicators['BB_Upper'] = bb_middle + (bb_std * 2)
        self.indicators['BB_Lower'] = bb_middle - (bb_std * 2)
        self.indicators['BB_Middle'] = bb_middle
        
        # 5. Stochastic
        lowest_14 = low.rolling(14).min()
        highest_14 = high.rolling(14).max()
        self.indicators['Stochastic'] = 100 * ((close - lowest_14) / (highest_14 - lowest_14))
        
        # 6. ATR (Average True Range)
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        self.indicators['ATR'] = tr.rolling(14).mean()
        
        # 7. OBV (On-Balance Volume)
        obv = (np.sign(close.diff()) * volume).cumsum()
        self.indicators['OBV'] = obv
        
        # 8. مؤشرات إضافية
        # Volume SMA
        self.indicators['Volume_SMA'] = volume.rolling(20).mean()
        self.indicators['Volume_Ratio'] = volume / self.indicators['Volume_SMA']
        
        # Price channels
        self.indicators['Upper_Channel'] = close.rolling(20).mean() + (close.rolling(20).std() * 2)
        self.indicators['Lower_Channel'] = close.rolling(20).mean() - (close.rolling(20).std() * 2)
        
        return self.indicators
    
    def analyze_trend(self) -> dict:
        """تحليل الاتجاه"""
        if self.df.empty or not self.indicators:
            return {'trend': 'N/A', 'rsi_value': 0, 'macd_signal': 'N/A'}
        
        close = self.df['Close']
        latest = close.iloc[-1]
        
        # تحديد الاتجاه الرئيسي
        if 'SMA_20' in self.indicators and 'SMA_50' in self.indicators:
            sma20 = self.indicators['SMA_20'].iloc[-1]
            sma50 = self.indicators['SMA_50'].iloc[-1]
            
            if latest > sma20 > sma50:
                trend = "صاعد قوي 🚀"
                trend_score = 3
            elif latest > sma20 and latest > sma50:
                trend = "صاعد 📈"
                trend_score = 2
            elif latest < sma20 < sma50:
                trend = "هابط قوي 📉"
                trend_score = -3
            elif latest < sma20 and latest < sma50:
                trend = "هابط 📉"
                trend_score = -2
            else:
                trend = "محايد ➡️"
                trend_score = 0
        else:
            trend = "غير محدد"
            trend_score = 0
        
        # RSI
        rsi_value = self.indicators['RSI'].iloc[-1] if 'RSI' in self.indicators else 50
        
        # MACD Signal
        if 'MACD' in self.indicators and 'Signal' in self.indicators:
            macd = self.indicators['MACD'].iloc[-1]
            signal = self.indicators['Signal'].iloc[-1]
            
            if macd > signal and macd > 0:
                macd_signal = "شراء قوي 🔥"
                macd_score = 2
            elif macd > signal:
                macd_signal = "شراء 📈"
                macd_score = 1
            elif macd < signal and macd < 0:
                macd_signal = "بيع قوي 🚨"
                macd_score = -2
            elif macd < signal:
                macd_signal = "بيع 📉"
                macd_score = -1
            else:
                macd_signal = "محايد ➡️"
                macd_score = 0
        else:
            macd_signal = "N/A"
            macd_score = 0
        
        # بولينجر باندز
        if 'BB_Upper' in self.indicators and 'BB_Lower' in self.indicators:
            bb_upper = self.indicators['BB_Upper'].iloc[-1]
            bb_lower = self.indicators['BB_Lower'].iloc[-1]
            
            if latest > bb_upper:
                bb_signal = "فوق النطاق العلوي - تشبع شراء"
                bb_score = -1
            elif latest < bb_lower:
                bb_signal = "تحت النطاق السفلي - تشبع بيع"
                bb_score = 2
            else:
                bb_signal = "داخل النطاق"
                bb_score = 1
        else:
            bb_signal = "N/A"
            bb_score = 0
        
        # Stochastic
        if 'Stochastic' in self.indicators:
            stoch = self.indicators['Stochastic'].iloc[-1]
            if stoch > 80:
                stoch_signal = "تشبع شراء"
                stoch_score = -1
            elif stoch < 20:
                stoch_signal = "تشبع بيع"
                stoch_score = 2
            else:
                stoch_signal = "محايد"
                stoch_score = 0
        else:
            stoch_signal = "N/A"
            stoch_score = 0
        
        # الحجم
        if 'Volume_Ratio' in self.indicators:
            vol_ratio = self.indicators['Volume_Ratio'].iloc[-1]
            if vol_ratio > 2:
                vol_signal = "حجم مرتفع جداً 🔥"
                vol_score = 1
            elif vol_ratio > 1.5:
                vol_signal = "حجم مرتفع 📈"
                vol_score = 0.5
            elif vol_ratio < 0.5:
                vol_signal = "حجم منخفض 📉"
                vol_score = -0.5
            else:
                vol_signal = "حجم طبيعي"
                vol_score = 0
        else:
            vol_signal = "N/A"
            vol_score = 0
        
        # حساب النقاط الإجمالية
        total_score = trend_score + (1 if rsi_value < 30 else -1 if rsi_value > 70 else 0) + macd_score + bb_score + stoch_score + vol_score
        
        # تحديد التوصية النهائية
        if total_score >= 5:
            recommendation = "شراء قوي 🚀"
        elif total_score >= 3:
            recommendation = "شراء 📈"
        elif total_score >= 1:
            recommendation = "ميل للشراء ↗️"
        elif total_score >= -1:
            recommendation = "احتفاظ ⚖️"
        elif total_score >= -3:
            recommendation = "ميل للبيع ↘️"
        elif total_score >= -5:
            recommendation = "بيع 📉"
        else:
            recommendation = "بيع قوي 🚨"
        
        return {
            'trend': trend,
            'trend_score': trend_score,
            'rsi_value': rsi_value,
            'macd_signal': macd_signal,
            'macd_score': macd_score,
            'bb_signal': bb_signal,
            'bb_score': bb_score,
            'stoch_signal': stoch_signal,
            'stoch_score': stoch_score,
            'vol_signal': vol_signal,
            'vol_score': vol_score,
            'total_score': total_score,
            'recommendation': recommendation,
            'current_price': latest,
            'sma_20': self.indicators['SMA_20'].iloc[-1] if 'SMA_20' in self.indicators else None,
            'sma_50': self.indicators['SMA_50'].iloc[-1] if 'SMA_50' in self.indicators else None,
            'sma_200': self.indicators['SMA_200'].iloc[-1] if 'SMA_200' in self.indicators else None,
        }

# ============= دوال تحليل متقدمة =============

def calculate_market_sentiment(df: pd.DataFrame) -> dict:
    """تحليل معنويات السوق"""
    if df.empty:
        return {}
    
    close = df['Close']
    returns = close.pct_change()
    
    # مؤشرات المخاطرة
    volatility = returns.std() * np.sqrt(252)  # التقلب السنوي
    sharpe = (returns.mean() * 252) / (volatility + 0.001)  # نسبة شارب
    
    # مؤشرات الزخم
    momentum_20 = (close.iloc[-1] / close.iloc[-21] - 1) * 100 if len(close) > 20 else 0
    momentum_50 = (close.iloc[-1] / close.iloc[-51] - 1) * 100 if len(close) > 50 else 0
    
    # حجم التداول
    avg_volume = df['Volume'].mean()
    latest_volume = df['Volume'].iloc[-1]
    volume_ratio = latest_volume / avg_volume if avg_volume > 0 else 1
    
    # نمو الأرباح
    returns_std = returns.std()
    var_95 = returns.quantile(0.05)  # 95% Value at Risk
    
    # نقاط القوة
    strength_score = 0
    strength_score += 1 if momentum_20 > 0 else -1 if momentum_20 < -5 else 0
    strength_score += 1 if momentum_50 > 0 else -1 if momentum_50 < -10 else 0
    strength_score += 1 if volume_ratio > 1.5 else -1 if volume_ratio < 0.5 else 0
    strength_score += 1 if volatility < 0.3 else -1 if volatility > 0.5 else 0
    
    if strength_score >= 3:
        sentiment = "إيجابي قوي 📈"
    elif strength_score >= 1:
        sentiment = "إيجابي ↗️"
    elif strength_score >= -1:
        sentiment = "محايد ➡️"
    elif strength_score >= -3:
        sentiment = "سلبي ↘️"
    else:
        sentiment = "سلبي قوي 📉"
    
    return {
        'volatility': volatility,
        'sharpe_ratio': sharpe,
        'momentum_20': momentum_20,
        'momentum_50': momentum_50,
        'volume_ratio': volume_ratio,
        'var_95': var_95,
        'sentiment': sentiment,
        'strength_score': strength_score,
        'avg_volume': avg_volume,
        'latest_volume': latest_volume
    }

def create_advanced_chart(df: pd.DataFrame, indicators: dict, symbol: str) -> go.Figure:
    """إنشاء رسم بياني متقدم مع جميع المؤشرات"""
    
    if df.empty:
        return go.Figure()
    
    fig = make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.35, 0.15, 0.15, 0.15, 0.2],
        subplot_titles=(
            f'{symbol} - السعر والمؤشرات',
            'حجم التداول',
            'RSI',
            'MACD',
            'Stochastic'
        )
    )
    
    # الرسم الرئيسي - الشموع والمتوسطات
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='شموع',
            increasing_line_color='#00cc00',
            decreasing_line_color='#ff3333'
        ),
        row=1, col=1
    )
    
    # إضافة المتوسطات المتحركة
    if indicators:
        for ma, color, width in [('SMA_20', 'orange', 2), ('SMA_50', 'blue', 2), ('SMA_200', 'purple', 2)]:
            if ma in indicators and not indicators[ma].isna().all():
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=indicators[ma],
                        name=ma,
                        line=dict(color=color, width=width)
                    ),
                    row=1, col=1
                )
    
    # بولينجر باندز
    if 'BB_Upper' in indicators and 'BB_Lower' in indicators:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=indicators['BB_Upper'],
                name='BB Upper',
                line=dict(color='gray', width=1, dash='dash')
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=indicators['BB_Lower'],
                name='BB Lower',
                line=dict(color='gray', width=1, dash='dash'),
                fill='tonexty',
                fillcolor='rgba(128, 128, 128, 0.1)'
            ),
            row=1, col=1
        )
    
    # حجم التداول
    colors = ['#00cc00' if close >= open else '#ff3333' 
              for close, open in zip(df['Close'], df['Open'])]
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7
        ),
        row=2, col=1
    )
    
    # RSI
    if 'RSI' in indicators:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=indicators['RSI'],
                name='RSI',
                line=dict(color='purple', width=2)
            ),
            row=3, col=1
        )
        # خطوط RSI
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    # MACD
    if 'MACD' in indicators and 'Signal' in indicators:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=indicators['MACD'],
                name='MACD',
                line=dict(color='blue', width=2)
            ),
            row=4, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=indicators['Signal'],
                name='Signal',
                line=dict(color='red', width=2)
            ),
            row=4, col=1
        )
        # هيستوغرام MACD
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=indicators['MACD_Hist'],
                name='MACD Hist',
                marker_color=['#00cc00' if val >= 0 else '#ff3333' for val in indicators['MACD_Hist']],
                opacity=0.5
            ),
            row=4, col=1
        )
    
    # Stochastic
    if 'Stochastic' in indicators:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=indicators['Stochastic'],
                name='Stochastic',
                line=dict(color='orange', width=2)
            ),
            row=5, col=1
        )
        fig.add_hline(y=80, line_dash="dash", line_color="red", row=5, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="green", row=5, col=1)
    
    # تحديث التنسيق
    fig.update_layout(
        height=1200,
        template='plotly_dark',
        showlegend=True,
        hovermode='x unified',
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # تحديث المحاور
    fig.update_yaxes(title_text="السعر ($)", row=1, col=1)
    fig.update_yaxes(title_text="الحجم", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
    fig.update_yaxes(title_text="MACD", row=4, col=1)
    fig.update_yaxes(title_text="Stochastic", row=5, col=1, range=[0, 100])
    
    return fig

def generate_ai_insights(analysis: dict, sentiment: dict, info: dict) -> str:
    """توليد رؤى ذكاء اصطناعي مخصصة"""
    
    insights = []
    
    # رؤى الاتجاه
    trend = analysis.get('trend', 'غير محدد')
    insights.append(f"📊 **الاتجاه العام:** {trend}")
    
    # رؤى RSI
    rsi = analysis.get('rsi_value', 50)
    if rsi < 30:
        insights.append(f"🟢 **RSI ({rsi:.1f}):** السهم في منطقة تشبع بيع، قد تكون فرصة شراء جيدة.")
    elif rsi > 70:
        insights.append(f"🔴 **RSI ({rsi:.1f}):** السهم في منطقة تشبع شراء، قد يكون هناك تصحيح قريب.")
    else:
        insights.append(f"🟡 **RSI ({rsi:.1f}):** السهم في منطقة محايدة، لا توجد إشارة قوية.")
    
    # رؤى MACD
    macd = analysis.get('macd_signal', 'N/A')
    insights.append(f"📈 **إشارة MACD:** {macd}")
    
    # رؤى البولينجر
    bb = analysis.get('bb_signal', 'N/A')
    if bb != 'N/A':
        insights.append(f"📊 **بولينجر باندز:** {bb}")
    
    # رؤى الحجم
    vol_ratio = sentiment.get('volume_ratio', 1)
    if vol_ratio > 1.5:
        insights.append(f"📊 **حجم التداول:** مرتفع ({vol_ratio:.2f}x المتوسط) - اهتمام قوي من السوق.")
    elif vol_ratio < 0.5:
        insights.append(f"📊 **حجم التداول:** منخفض ({vol_ratio:.2f}x المتوسط) - اهتمام ضعيف.")
    
    # رؤى التقلب
    volatility = sentiment.get('volatility', 0)
    if volatility > 0.5:
        insights.append(f"⚠️ **التقلب:** مرتفع جداً ({volatility:.2%}) - مخاطرة عالية.")
    elif volatility > 0.3:
        insights.append(f"⚖️ **التقلب:** متوسط ({volatility:.2%})")
    else:
        insights.append(f"✅ **التقلب:** منخفض ({volatility:.2%}) - استقرار نسبي.")
    
    # معلومات أساسية
    if info:
        sector = info.get('sector', 'غير محدد')
        market_cap = info.get('marketCap', 0)
        pe = info.get('trailingPE', 'N/A')
        
        insights.append(f"🏭 **القطاع:** {sector}")
        insights.append(f"💰 **القيمة السوقية:** ${market_cap/1e9:.2f}B" if market_cap else "")
        insights.append(f"📊 **مكرر الأرباح (P/E):** {pe:.2f}" if isinstance(pe, (int, float)) else "")
    
    # التوصية النهائية
    recommendation = analysis.get('recommendation', 'احتفاظ')
    insights.append(f"\n🎯 **توصية الذكاء الاصطناعي:** {recommendation}")
    insights.append(f"⭐ **نقاط القوة:** {analysis.get('total_score', 0)}/10")
    
    return "\n\n".join(insights)

# ============= الواجهة الرئيسية =============

# إعداد الصفحة
st.set_page_config(
    page_title="🤖 AI Market Insights",
    page_icon="🧠",
    layout="wide"
)

# تحميل CSS
css_path = os.path.join(ROOT_DIR, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🤖 AI Market Insights & Deep Analytics")
st.markdown("---")

# إدخال رمز السهم
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    symbol = st.text_input(
        "🔍 أدخل رمز السهم الأمريكي:",
        value="NVDA",
        help="مثال: AAPL, MSFT, GOOGL, TSLA, NVDA"
    ).upper()
    
    # اختيار سريع
    quick_symbols = ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META"]
    quick_select = st.selectbox("⚡ اختيار سريع:", quick_symbols, index=0)
    if quick_select != symbol:
        symbol = quick_select

with col2:
    period = st.selectbox(
        "📅 الفترة الزمنية:",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=2
    )

with col3:
    analysis_depth = st.select_slider(
        "🔬 عمق التحليل:",
        options=["أساسي", "متوسط", "متقدم", "شامل"],
        value="متقدم"
    )

st.markdown("---")

# تنفيذ التحليل
if symbol:
    with st.spinner(f"🧠 جاري تحليل {symbol} بتقنيات الذكاء الاصطناعي..."):
        # جلب البيانات
        provider = USMarketDataProvider(symbol)
        df = provider.get_history(period=period)
        info = provider.get_info()
        
        if df.empty:
            st.error(f"❌ لا يمكن جلب البيانات للسهم {symbol}. تأكد من صحة الرمز.")
        else:
            # التحليل الفني
            analyzer = TechnicalAnalyzer(df)
            indicators = analyzer.calculate_all_indicators()
            analysis = analyzer.analyze_trend()
            
            # تحليل معنويات السوق
            sentiment = calculate_market_sentiment(df)
            
            # ===== عرض النتائج =====
            
            # بطاقات المعلومات الرئيسية
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "📈 الاتجاه",
                    analysis.get('trend', 'N/A'),
                    delta=f"نقاط: {analysis.get('trend_score', 0)}"
                )
            
            with col2:
                st.metric(
                    "📊 RSI",
                    f"{analysis.get('rsi_value', 0):.1f}",
                    delta="تشبع بيع" if analysis.get('rsi_value', 50) < 30 else "تشبع شراء" if analysis.get('rsi_value', 50) > 70 else "محايد"
                )
            
            with col3:
                st.metric(
                    "🎯 التوصية",
                    analysis.get('recommendation', 'احتفاظ'),
                    delta=f"نقاط: {analysis.get('total_score', 0)}"
                )
            
            with col4:
                sentiment_text = sentiment.get('sentiment', 'محايد')
                st.metric(
                    "🧠 معنويات السوق",
                    sentiment_text,
                    delta=f"نقاط: {sentiment.get('strength_score', 0)}"
                )
            
            st.divider()
            
            # ===== الرؤى الذكية =====
            st.subheader("🧠 رؤى الذكاء الاصطناعي")
            
            insights = generate_ai_insights(analysis, sentiment, info)
            st.markdown(insights)
            
            st.divider()
            
            # ===== عرض المؤشرات في بطاقات =====
            st.subheader("📊 المؤشرات الفنية التفصيلية")
            
            # صف أول
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "📊 RSI",
                    f"{analysis.get('rsi_value', 0):.1f}",
                    delta="مفرط البيع" if analysis.get('rsi_value', 50) < 30 else "مفرط الشراء" if analysis.get('rsi_value', 50) > 70 else "محايد"
                )
            
            with col2:
                macd = analysis.get('macd_signal', 'N/A')
                macd_icon = "🔥" if "قوي" in macd else "📈" if "شراء" in macd else "📉" if "بيع" in macd else "➡️"
                st.metric(
                    "📈 MACD",
                    f"{macd_icon} {macd}",
                    delta=f"نقاط: {analysis.get('macd_score', 0)}"
                )
            
            with col3:
                st.metric(
                    "📊 Stochastic",
                    f"{analysis.get('stoch_signal', 'N/A')}",
                    delta=f"نقاط: {analysis.get('stoch_score', 0)}"
                )
            
            with col4:
                st.metric(
                    "📊 Bollinger Bands",
                    f"{analysis.get('bb_signal', 'N/A')}",
                    delta=f"نقاط: {analysis.get('bb_score', 0)}"
                )
            
            # صف ثاني
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "📊 SMA 20",
                    f"${analysis.get('sma_20', 0):.2f}" if analysis.get('sma_20') else "N/A"
                )
            
            with col2:
                st.metric(
                    "📊 SMA 50",
                    f"${analysis.get('sma_50', 0):.2f}" if analysis.get('sma_50') else "N/A"
                )
            
            with col3:
                st.metric(
                    "📊 SMA 200",
                    f"${analysis.get('sma_200', 0):.2f}" if analysis.get('sma_200') else "N/A"
                )
            
            with col4:
                st.metric(
                    "📊 السعر الحالي",
                    f"${analysis.get('current_price', 0):.2f}"
                )
            
            st.divider()
            
            # ===== الرسم البياني المتقدم =====
            st.subheader("📈 التحليل البياني المتقدم")
            
            # خيارات الرسم
            col1, col2 = st.columns(2)
            with col1:
                chart_height = st.slider("📏 ارتفاع الرسم:", 800, 1500, 1200, 100)
            with col2:
                show_indicators = st.multiselect(
                    "📊 إظهار المؤشرات:",
                    ["SMA 20", "SMA 50", "SMA 200", "بولينجر باندز", "RSI", "MACD", "Stochastic"],
                    default=["SMA 20", "SMA 50", "RSI", "MACD"]
                )
            
            # إنشاء الرسم البياني
            fig = create_advanced_chart(df, indicators, symbol)
            fig.update_layout(height=chart_height)
            st.plotly_chart(fig, use_container_width=True)
            
            # ===== إحصائيات السوق =====
            st.divider()
            st.subheader("📊 إحصائيات السوق المتقدمة")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                volatility = sentiment.get('volatility', 0) * 100
                st.metric(
                    "📊 التقلب السنوي",
                    f"{volatility:.1f}%",
                    delta="مرتفع" if volatility > 50 else "متوسط" if volatility > 30 else "منخفض"
                )
            
            with col2:
                sharpe = sentiment.get('sharpe_ratio', 0)
                st.metric(
                    "📊 نسبة شارب",
                    f"{sharpe:.2f}",
                    delta="جيد" if sharpe > 1 else "مقبول" if sharpe > 0.5 else "ضعيف"
                )
            
            with col3:
                vol_ratio = sentiment.get('volume_ratio', 1)
                st.metric(
                    "📊 نسبة الحجم",
                    f"{vol_ratio:.2f}x",
                    delta="مرتفع" if vol_ratio > 1.5 else "طبيعي" if vol_ratio > 0.5 else "منخفض"
                )
            
            with col4:
                momentum = sentiment.get('momentum_20', 0)
                st.metric(
                    "📊 الزخم (20 يوم)",
                    f"{momentum:+.1f}%",
                    delta="إيجابي" if momentum > 0 else "سلبي"
                )
            
            # ===== عرض البيانات =====
            st.divider()
            with st.expander("📋 عرض البيانات التاريخية"):
                st.dataframe(
                    df.tail(30).style.format({
                        'Open': '${:.2f}',
                        'High': '${:.2f}',
                        'Low': '${:.2f}',
                        'Close': '${:.2f}',
                        'Volume': '{:,.0f}'
                    }),
                    use_container_width=True
                )
            
            # معلومات إضافية
            st.divider()
            st.caption(f"🔄 آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.caption("📊 البيانات مقدمة من Yahoo Finance | 🤖 Powered by AI")
            
else:
    st.info("🔍 أدخل رمز السهم للبدء في تحليل الذكاء الاصطناعي")

# ===== الشريط الجانبي =====
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/artificial-intelligence.png", width=80)
    st.title("🧠 AI Insights")
    st.caption("تحليلات متقدمة بالذكاء الاصطناعي")
    st.divider()
    
    st.subheader("ℹ️ عن التحليل")
    st.write("""
    **المؤشرات المستخدمة:**
    - 📊 RSI (14)
    - 📈 MACD (12, 26, 9)
    - 📊 بولينجر باندز (20, 2)
    - 📈 Stochastic (14)
    - 📊 ATR (14)
    - 📈 OBV
    - 📊 المتوسطات المتحركة
    
    **نظام التقييم:**
    - 10 نقاط كحد أقصى
    - نقاط > 5: شراء قوي
    - نقاط 3-5: شراء
    - نقاط 1-3: ميل للشراء
    - نقاط -1 إلى 1: احتفاظ
    - نقاط -3 إلى -1: ميل للبيع
    - نقاط -5 إلى -3: بيع
    - نقاط < -5: بيع قوي
    """)
    
    st.divider()
    
    with st.expander("💡 نصائح"):
        st.markdown("""
        ✅ **نصائح للاستخدام:**
        1. اجمع بين التحليل الفني والأساسي
        2. استخدم التوصيات كأداة مساعدة
        3. راجع عدة مؤشرات قبل اتخاذ القرار
        4. انتبه لإشارات التباعد
        5. لا تعتمد على مؤشر واحد فقط
        """)
    
    st.divider()
    st.caption("© 2026 ByToBy-Pro4")
