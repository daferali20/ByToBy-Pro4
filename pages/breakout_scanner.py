import pandas as pd
import numpy as np
import yfinance as yf

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """حساب مؤشر RSI باستخدام pandas و numpy فقط دون الحاجة لمكتبات خارجية"""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_breakout_candidates():
    """
    محرك فحص الأسهم المستقل 100% عن pandas_ta لتفادي أخطاء السيرفرات
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
            
            close = df['Close']
            
            # 1. حساب Bollinger Bands يدوياً
            sma_20 = close.rolling(window=20).mean()
            std_20 = close.rolling(window=20).std()
            bb_upper = sma_20 + (std_20 * 2)
            bb_lower = sma_20 - (std_20 * 2)
            
            bandwidth = (bb_upper - bb_lower) / sma_20
            current_bandwidth = bandwidth.iloc[-1]
            min_bandwidth_50 = bandwidth.iloc[-50:].min()
            
            # شرط الانضغاط (Squeeze)
            is_squeeze = current_bandwidth <= (min_bandwidth_50 * 1.20)
            
            # 2. حساب حجم التداول غير الطبيعي (Unusual Volume)
            avg_volume_20 = df['Volume'].iloc[-20:].mean()
            current_volume = df['Volume'].iloc[-1]
            vol_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1.0
            unusual_volume = vol_ratio >= 1.5
            
            # 3. حساب RSI
            rsi_series = calculate_rsi(close)
            current_rsi = rsi_series.iloc[-1] if not np.isnan(rsi_series.iloc[-1]) else 50.0
            
            # 4. القرب من الأعلى
            high_52w = df['High'].max()
            current_price = close.iloc[-1]
            near_high_ratio = current_price / high_52w
            
            # 5. حساب درجة الجاهزية (Breakout Score)
            score = 40
            if is_squeeze: score += 25
            if unusual_volume: score += 20
            if near_high_ratio >= 0.88: score += 10
            if 50 <= current_rsi <= 70: score += 5
            
            # النقاط الفنية
            entry_price = round(current_price * 1.01, 2)
            stop_loss = round(current_price * 0.94, 2)
            target_1 = round(current_price * 1.15, 2)
            target_2 = round(current_price * 1.30, 2)
            
            results.append({
                "Symbol": symbol,
                "Current Price": round(current_price, 2),
                "Breakout Score": int(min(score, 99)),
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
        except Exception:
            continue
            
    res_df = pd.DataFrame(results)
    if not res_df.empty:
        res_df = res_df.sort_values(by="Breakout Score", ascending=False).reset_index(drop=True)
    return res_df
