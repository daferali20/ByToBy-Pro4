class StockRatingEngine:
    def __init__(self, rsi: float, pe_ratio: float, profit_margin: float, trend: str):
        self.rsi = rsi
        self.pe = pe_ratio
        self.margin = profit_margin
        self.trend = trend

    def generate_rating(self) -> dict:
        """حساب النتيجة التجميعية وتقييم السهم"""
        score = 50 # البداية من المنتصف

        # 1. RSI Scoring
        if 40 <= self.rsi <= 60:
            score += 10
        elif self.rsi < 30:
            score += 15 # فرصة دخول
        elif self.rsi > 70:
            score -= 15

        # 2. P/E Ratio Scoring
        if 0 < self.pe <= 15:
            score += 20
        elif 15 < self.pe <= 25:
            score += 10
        elif self.pe > 35:
            score -= 10

        # 3. Profit Margin Scoring
        if self.margin >= 0.15: # 15%+
            score += 15

        # 4. Technical Trend
        if "صاعد" in self.trend or "Bullish" in self.trend:
            score += 10
        else:
            score -= 10

        # Boundary Cap (0 - 100)
        final_score = max(0, min(100, score))

        if final_score >= 75:
            rating_label = "ممتاز (Strong Buy) 🚀"
        elif final_score >= 60:
            rating_label = "جيد (Buy) 🟢"
        elif final_score >= 40:
            rating_label = "محايد (Hold) ⚪"
        else:
            rating_label = "ضعيف (Sell) 🔴"

        return {
            "overall_score": final_score,
            "rating_label": rating_label
        }
