# backend/analysis/charts.py

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def build_advanced_stock_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    """إنشاء رسم بياني تفاعلي احترافي متعدد المحاور للأسهم الأمريكية"""
    
    # إنشاء لوحة من قطاعين (الشارت الرئيسي + RSI/MACD)
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'📉 {symbol} - Price & Moving Averages', '📊 Technical Indicators'),
        row_width=[0.3, 0.7]
    )

    # 1. رسم الشموع اليابانية (Candlestick)
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name="Price",
        increasing_line_color='#26a69a', 
        decreasing_line_color='#ef5350'
    ), row=1, col=1)

    # 2. إضافة المتوسطات المتحركة SMA 20 & SMA 50
    if 'SMA_20' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], mode='lines', name='SMA 20', line=dict(color='#ffb74d', width=1.5)), row=1, col=1)
    if 'SMA_50' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], mode='lines', name='SMA 50', line=dict(color='#29b6f6', width=1.5)), row=1, col=1)

    # 3. رسم مؤشر RSI في القطاع السفلي
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', name='RSI (14)', line=dict(color='#ab47bc', width=1.5)), row=2, col=1)
        
        # خطوط الذروة (Overbought 70 & Oversold 30)
        fig.add_hline(y=70, line_dash="dash", line_color="#ef5350", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#26a69a", row=2, col=1)

    # تحسين الهيكل البصري للشارت
    fig.update_layout(
        template="plotly_dark",
        height=620,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="#0d1117",
        plot_bgcolor="#161b22",
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig
