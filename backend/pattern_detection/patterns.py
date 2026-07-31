import pandas as pd

class PatternDetector:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def detect_bullish_engulfing(self) -> bool:
        """الكشف عن نموذج شمعة ابتلاعية إيجابية"""
        if len(self.df) < 2:
            return False
        
        prev = self.df.iloc[-2]
        curr = self.df.iloc[-1]

        # Prev candle red, Current candle green engulfing body
        prev_is_red = prev['Close'] < prev['Open']
        curr_is_green = curr['Close'] > curr['Open']

        if prev_is_red and curr_is_green:
            if curr['Open'] <= prev['Close'] and curr['Close'] >= prev['Open']:
                return True
        return False

    def detect_breakout(self, lookback: int = 20) -> bool:
        """الكشف عن اختراق أعلى قمة خلال فترة معينة"""
        if len(self.df) < lookback + 1:
            return False
        
        recent_high = self.df['High'].iloc[-(lookback+1):-1].max()
        last_close = self.df['Close'].iloc[-1]

        return last_close > recent_high
