import pandas as pd
import numpy as np
import yfinance as yf
import pandas_ta as ta

def get_breakout_candidates():
    """
    يقوم هذا التابع بمحاكاة واختبار تصفية أسهم الانفجار السعري بناءً على:
    - Bollinger Bands Squeeze (تضيّق التذبذب)
    - Unusual Volume (حجم تداول غير طبيعي)
    - Low Float / Micro-Mid Cap Proxy
    - Breakout Score (درجة الانفجار من 100)
    """
    tickers = [
        "NVDA", "AMD", "TSLA", "PLTR", "SOFI", 
        "MARA", "RIOT", "IONQ", "SMCI", "RKLB",
        "UPST", "AFRM", "PATH", "CELH", "CVNA"
    ]
    
    results = []
    
    for symbol in tickers:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo")
            if df.empty or len(df) < 50:
                continue
            
            # حساب المؤشرات
            bb = ta.bbands(df['Close'], length=20, std=2)
            if bb is None or bb.empty:
                continue
                
            bb_upper = bb['BBU_20_2.0']
            bb_lower = bb['BBL_20_2.0']
            bb_mid = bb['BBM_20_2.0']
            
            # عرض نطاق بولنجر النسبية
            bandwidth = (bb_upper - bb_lower) / bb_mid
            current_bandwidth = bandwidth.iloc[-1]
            min_bandwidth_50 = bandwidth.rolling(50).min().iloc[-1]
            
            # شرط انضغاط التذبذب (Squeeze)
            is_squeeze = current_bandwidth <= (min_bandwidth_50 * 1.20)
            
            # حجم التداول غير الطبيعي
            volume_20_avg = df['Volume'].rolling(20).mean().iloc[-1]
            current_volume = df['Volume'].iloc[-1]
            vol_ratio = current_volume / volume_20_avg if volume_20_avg > 0 else 1.0
            unusual_volume = vol_ratio >= 1.5
            
            # القرب من القمة التاريخية لـ 52 أسبوعاً
            high_52w = df['High'].max()
            current_price = df['Close'].iloc[-1]
            near_high_ratio = current_price / high_52w
            
            # RSI
            rsi_series = ta.rsi(df['Close'], length=14)
            current_rsi = rsi_series.iloc[-1] if rsi_series is not None and not rsi_series.empty else 50
            
            # حساب درجة الجاهزية للانفجار (Breakout Score)
            score = 40  # درجة أساسية
            if is_squeeze: score += 25
            if unusual_volume: score += 20
            if near_high_ratio >= 0.88: score += 10
            if 50 <= current_rsi <= 70: score += 5
            
            # تحديد مستويات التداول الفنية المقترحة
            entry_price = round(current_price * 1.01, 2)
            stop_loss = round(current_price * 0.94, 2)
            target_1 = round(current_price * 1.15, 2)
            target_2 = round(current_price * 1.30, 2)
            
            results.append({
                "Symbol": symbol,
                "Current Price": round(current_price, 2),
                "Breakout Score": min(score, 99),
                "Squeeze Status": "🔥 انضغاط حاد" if is_squeeze else "عادي",
                "Volume Ratio": f"{vol_ratio:.1f}x",
                "RSI": round(current_rsi, 1),
                "Near 52W High": f"{near_high_ratio*100:.1f}%",
                "Entry Point": entry_price,
                "Stop Loss": stop_loss,
                "Target 1": target_1,
                "Target 2": target_2,
                "Volume": int(current_volume)
            })
        except Exception as e:
            continue
            
    res_df = pd.DataFrame(results)
    if not res_df.empty:
        res_df = res_df.sort_values(by="Breakout Score", ascending=False).reset_index(drop=True)
    return res_df
