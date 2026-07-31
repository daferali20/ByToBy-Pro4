from typing import List, Dict
from backend.data_providers.market_data import MarketDataProvider
from backend.analysis.technical import TechnicalAnalyzer

class SmartScanner:
    def __init__(self, symbols: List[str]):
        self.symbols = symbols

    def scan_market(self, min_rsi: float = 0, max_rsi: float = 100, trend_filter: str = "الكل") -> List[Dict]:
        """مسح قائمة الأسهم وإرجاع المتوافق مع الفلتر"""
        results = []
        for sym in self.symbols:
            provider = MarketDataProvider(sym)
            df = provider.get_history(period="6mo")
            if df.empty:
                continue

            analyzer = TechnicalAnalyzer(df)
            analysis = analyzer.analyze_trend()

            rsi = analysis.get("rsi_value", 50)
            trend = analysis.get("trend", "")

            # Filter Condition logic
            if min_rsi <= rsi <= max_rsi:
                if trend_filter == "الكل" or (trend_filter in trend):
                    results.append({
                        "symbol": sym,
                        "close": analysis["last_close"],
                        "rsi": rsi,
                        "trend": trend,
                        "macd_signal": analysis["macd_signal"]
                    })
        return results
