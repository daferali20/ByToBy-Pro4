import pandas as pd

class TechnicalAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def analyze_trend(self) -> dict:
        """تحليل الاتجاه والمستويات الحرجة"""
        if self.df.empty or 'RSI' not in self.df.columns:
            return {"trend": "غير معروف", "rsi_status": "غير متوفر"}

        last_row = self.df.iloc[-1]
        prev_row = self.df.iloc[-2]

        # Trend check using Moving Averages
        if last_row['Close'] > last_row['SMA_50']:
            trend = "صاعد (Bullish) 🟢"
        else:
            trend = "هابط (Bearish) 🔴"

        # RSI Condition
        rsi = last_row['RSI']
        if rsi >= 70:
            rsi_status = "تشبع شرائي (Overbought) ⚠️"
        elif rsi <= 30:
            rsi_status = "تشبع بيعي (Oversold) 🎯"
        else:
            rsi_status = "محايد (Neutral) ⚪"

        # MACD Signal Line Crossover
        macd_cross = "لا يوجد"
        if prev_row['MACD'] < prev_row['MACD_Signal'] and last_row['MACD'] > last_row['MACD_Signal']:
            macd_cross = "تقاطع إيجابي (Buy Signal) 🚀"
        elif prev_row['MACD'] > prev_row['MACD_Signal'] and last_row['MACD'] < last_row['MACD_Signal']:
            macd_cross = "تقاطع سلبي (Sell Signal) 🔻"

        return {
            "trend": trend,
            "rsi_value": round(rsi, 2),
            "rsi_status": rsi_status,
            "macd_signal": macd_cross,
            "last_close": round(last_row['Close'], 2)
        }
