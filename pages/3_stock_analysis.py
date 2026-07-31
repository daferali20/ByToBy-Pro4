import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.title("🔬 التحليل الشامل للسهم | Stock Analysis")

symbol = st.text_input("أدخل رمز السهم (مثال: 2222.SR أو AAPL):", value="2222.SR")

if symbol:
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="6mo")
        info = ticker.info
        
        st.subheader(f"تحليل سهم: {info.get('longName', symbol)}")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("السعر الحالي", f"{df['Close'].iloc[-1]:.2f}")
        col2.metric("أعلى سعر (6 أشهر)", f"{df['High'].max():.2f}")
        col3.metric("أدنى سعر (6 أشهر)", f"{df['Low'].min():.2f}")
        col4.metric("المتوسط المتحرك 50", f"{df['Close'].rolling(50).mean().iloc[-1]:.2f}")

        # Plotly Candlestick with MA
        df['MA50'] = df['Close'].rolling(50).mean()
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
        fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], mode='lines', name='MA 50', line=dict(color='orange')))
        
        fig.update_layout(template="plotly_dark", height=500)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"خطأ في جلب بيانات السهم: {e}")
