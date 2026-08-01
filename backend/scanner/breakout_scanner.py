import pandas as pd
import pandas_ta as ta

def scan_for_potential_breakouts(df: pd.DataFrame):
    """
    df يحتوي على البيانات اليومية للسهم: Open, High, Low, Close, Volume
    """
    # 1. حساب Bollinger Bands للتأكد من انضغاط التذبذب (Squeeze)
    bb = ta.bbands(df['Close'], length=20, std=2)
    band_width = (bb['BBU_20_2.0'] - bb['BBL_20_2.0']) / bb['BBM_20_2.0']
    
    is_squeeze = band_width.iloc[-1] < band_width.rolling(50).min().iloc[-1] * 1.15
    
    # 2. حساب متوسط حجم التداول غير الطبيعي (Unusual Volume)
    avg_volume_20 = df['Volume'].rolling(20).mean()
    unusual_volume = df['Volume'].iloc[-1] > (avg_volume_20.iloc[-1] * 2.5)
    
    # 3. حساب قوة الاتجاه (RSI بين 50 و 65 - بداية انطلاق)
    rsi = ta.rsi(df['Close'], length=14).iloc[-1]
    healthy_rsi = 50 <= rsi <= 68
    
    # 4. القرب من أعلى سعر 52 أسبوع
    high_52w = df['High'].rolling(252).max().iloc[-1]
    near_high = df['Close'].iloc[-1] >= (high_52w * 0.92)
    
    # النتيجة: السهم جاهز للانفجار
    is_breakout_candidate = is_squeeze and unusual_volume and healthy_rsi and near_high
    
    return is_breakout_candidate
