class FairValueCalculator:
    def __init__(self, eps: float, growth_rate: float, pe_ratio: float):
        self.eps = eps                     # ربحية السهم (Earnings Per Share)
        self.growth_rate = growth_rate     # معدل النمو المتوقع (%)
        self.pe_ratio = pe_ratio           # مكرر الربحية المستهدف

    def calculate_dcf_fair_value(self, discount_rate: float = 0.10, years: int = 5) -> float:
        """حساب القيمة العادلة التقريبية بالتدفقات النقدية المخصومة"""
        future_eps = self.eps
        total_present_value = 0.0

        for year in range(1, years + 1):
            future_eps *= (1 + self.growth_rate)
            pv = future_eps / ((1 + discount_rate) ** year)
            total_present_value += pv

        # Terminal Value Estimate
        terminal_value = (future_eps * self.pe_ratio) / ((1 + discount_rate) ** years)
        fair_value = total_present_value + terminal_value
        
        return round(fair_value, 2)

    def evaluate_valuation(self, current_price: float) -> dict:
        """مقارنة السعر الحالي بالقيمة العادلة"""
        fair_val = self.calculate_dcf_fair_value()
        margin_of_safety = ((fair_val - current_price) / fair_val) * 100

        status = "سعر عادل"
        if margin_of_safety > 15:
            status = "مقوم بأقل من قيمته (Undervalued) 💎"
        elif margin_of_safety < -15:
            status = "مقوم بأعلى من قيمته (Overvalued) ⚠️"

        return {
            "current_price": current_price,
            "fair_value": fair_val,
            "margin_of_safety_pct": round(margin_of_safety, 2),
            "status": status
        }
