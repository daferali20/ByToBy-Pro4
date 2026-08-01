import pandas as pd
import numpy as np

def scan_for_potential_breakouts(df: pd.DataFrame) -> bool:
    """
    يفحص الكود ما إذا كان السهم متوافقاً مع شروط الانفجار السعري.
    يتطلب DataFrame يحتوي على الأسعار اليومية: Open, High, Low, Close, Volume
    """
    # 1. التأكد من كفاية البيانات للحسابات
    if df is None or len(df) < 50:
        return False

    try:
        close = df['Close']
        volume = df['Volume']
        
        # 2. حساب Bollinger Bands ينقّح من الاعتماد على pandas-ta
        sma_20 = close.rolling(window=20).mean()
        std_20 = close.rolling(window=20).std()
        
        bb_upper = sma_20 + (std_20 * 2)
        bb_lower = sma_20 - (std_20 * 2)
        
        # حساب عرض نطاق بولنجر (Bandwidth)
        band_width = (bb_upper - bb_lower) / sma_20
        
        current_bandwidth = band_width.iloc[-1]
        # حساب أدنى عرض نطاق في السلسلة السابقة (باستثناء الشمعة الحالية لتجنب التكرار الذاتي)
        min_bandwidth_prev = band_width.iloc[-51:-1].min()
        
        if pd.isna(current_bandwidth) or pd.isna(min_bandwidth_prev):
            return False

        # شرط انضغاط التذبذب (Squeeze)
        is_squeeze = current_bandwidth <= (min_bandwidth_prev * 1.20)

        # 3. حساب متوسط حجم التداول غير الطبيعي (Unusual Volume)
        avg_volume_20 = volume.iloc[-21:-1].mean()  # المتوسط لـ 20 يوم قبل الشمعة الحالية
        current_volume = volume.iloc[-1]
        
        unusual_volume = (current_volume >= (avg_volume_20 * 2.0)) if avg_volume_20 > 0 else False

        # 4. حساب قوة الاتجاه (RSI) يدوياً بشكل آمن
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(window=14).mean()
        
        rs = gain / loss
        rsi_series = 100 - (100 / (1 + rs))
        rsi = rsi_series.iloc[-1]

        if pd.isna(rsi):
            healthy_rsi = False
        else:
            healthy_rsi = 50 <= rsi <= 70

        # 5. القرب من أعلى سعر (أعلى قمة في الفترة الأخيرة)
        lookback = min(len(df), 252)
        high_period = df['High'].iloc[-lookback:].max()
        current_price = close.iloc[-1]
        
        near_high = current_price >= (high_period * 0.88)  # مرونة أعلى 88% بدلاً من 92%

        # النتيجة النهائية
        return bool(is_squeeze and unusual_volume and healthy_rsi and near_high)

    except Exception as e:
        # طباعة الخطأ في التيرمنال لتسهيل التتبع والديباج بدلاً من التجاهل الصامت
        print(f"⚠️ خطأ أثناء تحليل دالة Breakout: {e}")
        return False
