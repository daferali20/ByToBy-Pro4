import pandas as pd
import pandas_ta as ta

def scan_for_potential_breakouts(df: pd.DataFrame) -> bool:
    """
    يفحص الكود ما إذا كان السهم متوافقاً مع شروط الانفجار السعري.
    يتطلب DataFrame يحتوي على الأسعار اليومية: Open, High, Low, Close, Volume
    """
    # التأكد من كفاية البيانات للحسابات
    if df is None or len(df) < 50:
        return False

    try:
        # 1. حساب Bollinger Bands بأسلوب آمن لتفادي تغيير أسماء الأعمدة
        bb = ta.bbands(df['Close'], length=20, std=2)
        if bb is None or bb.empty:
            return False
            
        # استخراج أعمدة BBU (العلوي) و BBL (السفلي) و BBM (الأوسط) ديناميكياً
        bbu_col = [c for c in bb.columns if c.startswith('BBU')][0]
        bbl_col = [c for c in bb.columns if c.startswith('BBL')][0]
        bbm_col = [c for c in bb.columns if c.startswith('BBM')][0]

        # حساب عرض نطاق بولنجر (Bandwidth)
        band_width = (bb[bbu_col] - bb[bbl_col]) / bb[bbm_col]
        
        current_bandwidth = band_width.iloc[-1]
        min_bandwidth_50 = band_width.iloc[-50:].min()  # حساب القاع في آخر 50 شمعة
        
        # شرط انضغاط التذبذب (Squeeze)
        is_squeeze = current_bandwidth <= (min_bandwidth_50 * 1.15)

        # 2. حساب متوسط حجم التداول غير الطبيعي (Unusual Volume)
        avg_volume_20 = df['Volume'].iloc[-20:].mean()
        current_volume = df['Volume'].iloc[-1]
        unusual_volume = current_volume >= (avg_volume_20 * 2.5) if avg_volume_20 > 0 else False

        # 3. حساب قوة الاتجاه (RSI)
        rsi_series = ta.rsi(df['Close'], length=14)
        if rsi_series is None or rsi_series.empty:
            return False
            
        rsi = rsi_series.iloc[-1]
        healthy_rsi = 50 <= rsi <= 68

        # 4. القرب من أعلى سعر (يتكيف مع طول البيانات حتى لو كانت أقل من سنة)
        lookback = min(len(df), 252)
        high_period = df['High'].iloc[-lookback:].max()
        current_price = df['Close'].iloc[-1]
        near_high = current_price >= (high_period * 0.92)

        # النتيجة النهائية
        return bool(is_squeeze and unusual_volume and healthy_rsi and near_high)

    except Exception:
        # في حال حدوث أي خطأ أثنـاء المعالجة يتم تخطي السهم بأمان
        return False
