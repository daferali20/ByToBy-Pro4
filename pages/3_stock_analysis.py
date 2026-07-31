# pages/3_stock_analysis.py

import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# إعداد المسار
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import yfinance as yf
import requests
from typing import Dict, Any, Optional

# ============= الخدمات والوحدات =============

class USStockService:
    """خدمة جلب بيانات الأسهم الأمريكية"""
    
    @staticmethod
    def get_full_stock_report(symbol: str) -> Dict[str, Any]:
        """جلب تقرير كامل عن السهم"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # جلب البيانات التاريخية
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                return {"error": f"لا توجد بيانات للسهم {symbol}"}
            
            # البيانات المباشرة
            current_price = info.get('regularMarketPrice', info.get('currentPrice', 0))
            previous_close = info.get('regularMarketPreviousClose', info.get('previousClose', 0))
            change = current_price - previous_close if current_price and previous_close else 0
            change_pct = (change / previous_close * 100) if previous_close else 0
            
            live_data = {
                'current_price': current_price,
                'change': change,
                'change_pct': change_pct,
                'volume': info.get('regularMarketVolume', 0),
                'day_high': info.get('dayHigh', 0),
                'day_low': info.get('dayLow', 0)
            }
            
            # البيانات الأساسية
            fundamentals = {
                'company_name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'eps': info.get('trailingEps', 'N/A'),
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                '52_week_low': info.get('fiftyTwoWeekLow', 0),
                'target_price': info.get('targetMeanPrice', 'N/A'),
                'beta': info.get('beta', 'N/A')
            }
            
            # البيانات الفنية
            technical = USStockService.calculate_technical_indicators(hist)
            
            return {
                'live': live_data,
                'fundamentals': fundamentals,
                'technical': technical,
                'df': hist
            }
            
        except Exception as e:
            return {"error": f"خطأ في جلب البيانات: {str(e)}"}
    
    @staticmethod
    def calculate_technical_indicators(df: pd.DataFrame) -> Dict[str, Any]:
        """حساب المؤشرات الفنية"""
        if df.empty:
            return {}
        
        close = df['Close']
        
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
        
        # تحديد الاتجاه
        current_close = close.iloc[-1]
        if current_close > sma_20.iloc[-1] > sma_50.iloc[-1]:
            trend = "صاعد قوي"
        elif current_close > sma_20.iloc[-1] and current_close > sma_50.iloc[-1]:
            trend = "صاعد"
        elif current_close < sma_20.iloc[-1] < sma_50.iloc[-1]:
            trend = "هابط قوي"
        elif current_close < sma_20.iloc[-1] and current_close < sma_50.iloc[-1]:
            trend = "هابط"
        else:
            trend = "محايد"
        
        # MACD
        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        macd_hist = macd - signal
        
        # بولينجر باندز
        bb_middle = close.rolling(window=20).mean()
        bb_std = close.rolling(window=20).std()
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)
        
        return {
            'rsi_value': rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50,
            'rsi_series': rsi,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'sma_200': sma_200,
            'trend': trend,
            'macd': macd,
            'macd_signal': signal,
            'macd_histogram': macd_hist,
            'bb_upper': bb_upper,
            'bb_lower': bb_lower,
            'bb_middle': bb_middle,
            'volume': df['Volume']
        }

class StockPricePredictor:
    """نموذج بسيط للتنبؤ بأسعار الأسهم"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.model = None
        
    def train_and_predict_next_day(self) -> Dict[str, Any]:
        """تدريب نموذج بسيط والتنبؤ باليوم التالي"""
        try:
            if self.df.empty or len(self.df) < 30:
                return {
                    'predicted_price': self.df['Close'].iloc[-1] if not self.df.empty else 0,
                    'confidence': 0,
                    'error': 'بيانات غير كافية'
                }
            
            # نموذج بسيط باستخدام المتوسطات المتحركة
            close = self.df['Close']
            sma_5 = close.rolling(window=5).mean()
            sma_10 = close.rolling(window=10).mean()
            
            # توقع بسيط: متوسط آخر 5 أيام مع ميل
            last_5 = close.iloc[-5:]
            trend = (last_5.iloc[-1] - last_5.iloc[0]) / 5 if len(last_5) > 1 else 0
            predicted = close.iloc[-1] + trend
            
            # حساب الثقة
            volatility = close.pct_change().std() * 100
            confidence = max(0, min(100, 100 - (volatility * 2)))
            
            return {
                'predicted_price': predicted,
                'current_price': close.iloc[-1],
                'confidence': min(confidence, 90),
                'trend': trend,
                'volatility': volatility
            }
            
        except Exception as e:
            return {
                'predicted_price': self.df['Close'].iloc[-1] if not self.df.empty else 0,
                'confidence': 0,
                'error': str(e)
            }

class RecommendationEngine:
    """محرك التوصيات الذكي"""
    
    @staticmethod
    def get_final_recommendation(
        symbol: str,
        current_price: float,
        rsi: float,
        pe: float,
        margin: float = 0.18,
        eps: float = 1.0,
        growth: float = 0.08,
        trend: str = "محايد"
    ) -> Dict[str, Any]:
        """توليد توصية استثمارية شاملة"""
        
        score = 0
        signals = []
        details = []
        
        # تحليل RSI
        if rsi < 30:
            score += 2
            signals.append("تشبع بيع - فرصة شراء")
            details.append(f"RSI منخفض ({rsi:.1f}) يشير إلى تشبع بيع")
        elif rsi < 40:
            score += 1
            signals.append("RSI منخفض نسبياً")
        elif rsi > 70:
            score -= 2
            signals.append("تشبع شراء - تجنب الشراء")
            details.append(f"RSI مرتفع ({rsi:.1f}) يشير إلى تشبع شراء")
        elif rsi > 60:
            score -= 1
            signals.append("RSI مرتفع نسبياً")
        else:
            score += 1
            signals.append("RSI في نطاق محايد")
        
        # تحليل الاتجاه
        if "صاعد" in trend:
            score += 2
            signals.append(f"الاتجاه {trend}")
        elif "هابط" in trend:
            score -= 1
            signals.append(f"الاتجاه {trend}")
        
        # تحليل السعر إلى القيمة العادلة
        if pe != 'N/A' and isinstance(pe, (int, float)):
            if pe < 15:
                score += 1
                signals.append("P/E أقل من متوسط السوق")
            elif pe > 30:
                score -= 1
                signals.append("P/E مرتفع")
        
        # تحليل النمو
        if growth > 0.1:
            score += 1
            signals.append(f"نمو قوي ({growth:.1%})")
        elif growth > 0.05:
            score += 0.5
        
        # تحديد التوصية النهائية
        if score >= 4:
            rating = "شراء قوي"
            action = "🚀 شراء"
            risk = "منخفض"
            summary = "فرصة استثمارية ممتازة مع إشارات قوية"
        elif score >= 2:
            rating = "شراء"
            action = "📈 شراء"
            risk = "متوسط"
            summary = "فرصة جيدة مع بعض المؤشرات الإيجابية"
        elif score >= 0:
            rating = "احتفاظ"
            action = "⚖️ احتفاظ"
            risk = "متوسط"
            summary = "احتفظ بالسهم وانتظر إشارات أفضل"
        elif score >= -2:
            rating = "بيع جزئي"
            action = "📉 بيع جزئي"
            risk = "مرتفع"
            summary = "انصح بتقليل المركز"
        else:
            rating = "بيع قوي"
            action = "🚨 بيع"
            risk = "مرتفع جداً"
            summary = "اتجاه سلبي قوي، انصح بالبيع"
        
        return {
            'rating': rating,
            'action': action,
            'risk': risk,
            'score': score,
            'signals': signals,
            'details': details,
            'action_summary': f"{action} - {summary}",
            'symbol': symbol,
            'current_price': current_price
        }

class AlertNotifier:
    """نظام إرسال التنبيهات"""
    
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        
    def send_telegram_alert(self, message: str) -> bool:
        """إرسال تنبيه عبر تلغرام"""
        try:
            if not self.token or not self.chat_id:
                return False
                
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except:
            return False

def build_advanced_stock_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    """إنشاء رسم بياني متقدم للأسهم"""
    
    if df is None or df.empty:
        return go.Figure()
    
    # حساب المؤشرات الفنية
    technical = USStockService.calculate_technical_indicators(df)
    
    # إنشاء رسم بياني متعدد
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f'{symbol} - السعر والمؤشرات', 'حجم التداول', 'MACD')
    )
    
    # إضافة شموع يابانية
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
    if 'sma_20' in technical:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=technical['sma_20'],
                name='SMA 20',
                line=dict(color='orange', width=1.5)
            ),
            row=1, col=1
        )
    
    if 'sma_50' in technical:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=technical['sma_50'],
                name='SMA 50',
                line=dict(color='blue', width=1.5)
            ),
            row=1, col=1
        )
    
    # إضافة بولينجر باندز
    if 'bb_upper' in technical and 'bb_lower' in technical:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=technical['bb_upper'],
                name='BB Upper',
                line=dict(color='gray', width=1, dash='dash')
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=technical['bb_lower'],
                name='BB Lower',
                line=dict(color='gray', width=1, dash='dash'),
                fill='tonexty',
                fillcolor='rgba(128, 128, 128, 0.1)'
            ),
            row=1, col=1
        )
    
    # إضافة حجم التداول
    colors = ['#00cc00' if close >= open else '#ff3333' 
              for close, open in zip(df['Close'], df['Open'])]
    
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='حجم التداول',
            marker_color=colors,
            opacity=0.7
        ),
        row=2, col=1
    )
    
    # إضافة MACD
    if 'macd' in technical and 'macd_signal' in technical:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=technical['macd'],
                name='MACD',
                line=dict(color='blue', width=1.5)
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=technical['macd_signal'],
                name='إشارة MACD',
                line=dict(color='red', width=1.5)
            ),
            row=3, col=1
        )
        
        # إضافة الهيستوغرام
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=technical['macd_histogram'],
                name='MACD Histogram',
                marker_color=['#00cc00' if val >= 0 else '#ff3333' for val in technical['macd_histogram']],
                opacity=0.5
            ),
            row=3, col=1
        )
    
    # تنسيق الرسم
    fig.update_layout(
        title=f'📊 تحليل {symbol} المتقدم',
        height=800,
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
    fig.update_xaxes(title_text="التاريخ", row=3, col=1)
    fig.update_yaxes(title_text="السعر ($)", row=1, col=1)
    fig.update_yaxes(title_text="الحجم", row=2, col=1)
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    
    return fig

# ============= الواجهة الرئيسية =============

# إعداد الصفحة
st.set_page_config(
    page_title="⚡ US Stock Terminal",
    page_icon="🇺🇸",
    layout="wide"
)

# تحميل CSS
css_path = os.path.join(ROOT_DIR, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# العنوان
st.title("⚡ ByToBy-Pro4 | US Stock Terminal")
st.markdown("---")

# شريط الإدخال
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    symbol_input = st.text_input(
        "🔍 أدخل رمز السهم:",
        value="NVDA",
        help="مثال: AAPL, MSFT, GOOGL, TSLA, NVDA"
    ).upper()
    
    # قائمة الأسهم الشهيرة للاختيار السريع
    popular_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "WMT"]
    quick_select = st.selectbox(
        "⚡ اختيار سريع:",
        popular_stocks,
        index=popular_stocks.index(symbol_input) if symbol_input in popular_stocks else 0
    )
    if quick_select != symbol_input:
        symbol_input = quick_select

with col2:
    st.markdown("### 📅 الفترة الزمنية")
    period_options = {
        "1 شهر": "1mo",
        "3 أشهر": "3mo",
        "6 أشهر": "6mo",
        "سنة": "1y",
        "سنتين": "2y",
        "5 سنوات": "5y"
    }
    selected_period = st.selectbox(
        "اختر الفترة:",
        list(period_options.keys()),
        index=3
    )

with col3:
    st.markdown("### 🔔 التنبيهات")
    tg_token = st.text_input("Telegram Token:", type="password", placeholder="اختياري")
    tg_chat_id = st.text_input("Chat ID:", type="password", placeholder="اختياري")

st.markdown("---")

# جلب البيانات وعرضها
if symbol_input:
    with st.spinner(f"🔄 جاري تحميل بيانات {symbol_input}..."):
        report = USStockService.get_full_stock_report(symbol_input)
    
    if "error" in report:
        st.error(f"❌ {report['error']}")
        st.info("💡 تأكد من صحة رمز السهم وجرب مرة أخرى")
    else:
        live = report["live"]
        fund = report["fundamentals"]
        tech = report["technical"]
        df = report["df"]
        
        # ===== بطاقات المعلومات الأساسية =====
        st.subheader(f"🏢 {fund.get('company_name', symbol_input)} ({symbol_input})")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            current_price = live.get('current_price', 0)
            change_pct = live.get('change_pct', 0)
            st.metric(
                "💰 السعر الحالي",
                f"${current_price:,.2f}" if current_price else "N/A",
                delta=f"{change_pct:+.2f}%" if change_pct else None,
                delta_color="normal"
            )
        
        with col2:
            pe = fund.get('pe_ratio', 'N/A')
            st.metric(
                "📈 P/E Ratio",
                f"{pe:.2f}" if isinstance(pe, (int, float)) else str(pe)
            )
        
        with col3:
            high = fund.get('52_week_high', 0)
            st.metric(
                "📊 52-Week High",
                f"${high:,.2f}" if high else "N/A"
            )
        
        with col4:
            low = fund.get('52_week_low', 0)
            st.metric(
                "📉 52-Week Low",
                f"${low:,.2f}" if low else "N/A"
            )
        
        # معلومات إضافية
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "🏭 القطاع",
                fund.get('sector', 'N/A')
            )
        with col2:
            st.metric(
                "💼 الصناعة",
                fund.get('industry', 'N/A')
            )
        with col3:
            market_cap = fund.get('market_cap', 0)
            st.metric(
                "💰 القيمة السوقية",
                f"${market_cap/1e9:.2f}B" if market_cap else "N/A"
            )
        with col4:
            dividend = fund.get('dividend_yield', 0)
            st.metric(
                "💸 عائد التوزيعات",
                f"{dividend:.2f}%" if dividend else "N/A"
            )
        
        st.divider()
        
        # ===== التنبؤ والتوصية =====
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🤖 الذكاء الاصطناعي - التنبؤ والتوصية")
            
            # التنبؤ بالسعر
            predictor = StockPricePredictor(df)
            pred_result = predictor.train_and_predict_next_day()
            
            if "error" not in pred_result:
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric(
                        "📊 السعر المتوقع",
                        f"${pred_result['predicted_price']:.2f}",
                        delta=f"${pred_result['predicted_price'] - pred_result['current_price']:.2f}"
                    )
                with col_b:
                    st.metric(
                        "🎯 الثقة",
                        f"{pred_result['confidence']:.1f}%",
                        delta=f"التقلب: {pred_result.get('volatility', 0):.2f}%"
                    )
                with col_c:
                    st.metric(
                        "📈 الاتجاه",
                        f"{pred_result.get('trend', 0):+.4f}",
                        delta="يومياً"
                    )
            else:
                st.warning(f"⚠️ {pred_result.get('error', 'تعذر التنبؤ')}")
            
            # التوصية
            rec = RecommendationEngine.get_final_recommendation(
                symbol=symbol_input,
                current_price=live.get('current_price', 0.0),
                rsi=tech.get('rsi_value', 50.0),
                pe=fund.get('pe_ratio') if isinstance(fund.get('pe_ratio'), (int, float)) else 20.0,
                margin=0.18,
                eps=fund.get('eps') if isinstance(fund.get('eps'), (int, float)) else 1.0,
                growth=0.08,
                trend=tech.get('trend', 'محايد')
            )
            
            # عرض التوصية بشكل مميز
            color = "🟢" if "شراء" in rec['rating'] else "🟡" if "احتفاظ" in rec['rating'] else "🔴"
            st.success(f"{color} **توصية الذكاء الاصطناعي:** {rec['action_summary']}")
            
            # عرض التفاصيل
            with st.expander("📋 تفاصيل التوصية"):
                st.write(f"**التقييم:** {rec['rating']}")
                st.write(f"**المخاطرة:** {rec['risk']}")
                st.write(f"**النقاط:** {rec['score']}/6")
                st.write("**الإشارات:**")
                for signal in rec['signals']:
                    st.write(f"- {signal}")
        
        with col2:
            st.subheader("📊 المؤشرات الفنية")
            
            # RSI مع مؤشر بصري
            rsi_value = tech.get('rsi_value', 50)
            rsi_color = "🟢" if rsi_value < 30 else "🔴" if rsi_value > 70 else "🟡"
            st.metric(
                "📊 RSI",
                f"{rsi_value:.1f}",
                delta=f"{rsi_color} {'تشبع بيع' if rsi_value < 30 else 'تشبع شراء' if rsi_value > 70 else 'محايد'}"
            )
            
            # الاتجاه
            trend = tech.get('trend', 'محايد')
            trend_icon = "📈" if "صاعد" in trend else "📉" if "هابط" in trend else "➡️"
            st.metric(
                "📈 الاتجاه",
                f"{trend_icon} {trend}"
            )
            
            # حجم التداول
            volume = live.get('volume', 0)
            st.metric(
                "📊 حجم التداول",
                f"{volume:,.0f}" if volume else "N/A"
            )
            
            # السعر المستهدف
            target = fund.get('target_price', 'N/A')
            if isinstance(target, (int, float)):
                upside = ((target - live.get('current_price', 0)) / live.get('current_price', 1) * 100) if live.get('current_price', 0) > 0 else 0
                st.metric(
                    "🎯 السعر المستهدف",
                    f"${target:.2f}",
                    delta=f"{upside:+.2f}%"
                )
            else:
                st.metric("🎯 السعر المستهدف", "غير متوفر")
        
        # ===== إرسال التنبيه =====
        if tg_token and tg_chat_id:
            st.divider()
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📲 إرسال التوصية إلى Telegram", use_container_width=True, type="primary"):
                    msg = f"""
🚨 <b>تنبيه ByToBy-Pro4</b>

📈 <b>السهم:</b> {symbol_input} - {fund.get('company_name', '')}
💵 <b>السعر الحالي:</b> ${live.get('current_price', 0):.2f}
📊 <b>التغير:</b> {live.get('change_pct', 0):+.2f}%

🎯 <b>توصية AI:</b> {rec['rating']}
📈 <b>RSI:</b> {tech.get('rsi_value', 50):.1f}
📊 <b>الاتجاه:</b> {tech.get('trend', 'محايد')}
💡 <b>التفاصيل:</b> {rec['action_summary']}

📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """
                    
                    notifier = AlertNotifier(tg_token, tg_chat_id)
                    if notifier.send_telegram_alert(msg):
                        st.success("✅ تم إرسال التنبيه إلى Telegram بنجاح!")
                    else:
                        st.error("❌ فشل إرسال التنبيه. تأكد من صحة التوكن ورقم الدردشة")
        
        # ===== الرسم البياني =====
        st.divider()
        st.subheader("📈 تحليل متقدم - رسم بياني تفاعلي")
        
        # خيارات الرسم البياني
        col1, col2 = st.columns(2)
        with col1:
            show_indicators = st.multiselect(
                "📊 إضافة مؤشرات:",
                ["SMA 20", "SMA 50", "بولينجر باندز", "MACD", "حجم التداول"],
                default=["SMA 20", "MACD"]
            )
        with col2:
            chart_height = st.slider("📏 ارتفاع الرسم البياني:", 400, 1000, 700, 50)
        
        # بناء الرسم البياني
        fig = build_advanced_stock_chart(df, symbol_input)
        
        # تحديث ارتفاع الرسم
        fig.update_layout(height=chart_height)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ===== البيانات الإضافية =====
        st.divider()
        with st.expander("📋 عرض البيانات الخام"):
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
        
        # ===== معلومات إضافية =====
        st.divider()
        st.caption(f"🔄 آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.caption("📊 البيانات مقدمة من Yahoo Finance | ⚡ ByToBy-Pro4")

else:
    st.info("🔍 أدخل رمز السهم للبدء في التحليل")
