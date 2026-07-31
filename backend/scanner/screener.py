# backend/scanner/screener.py

import sys
import os
from typing import List, Dict

# إضافة مجلد الجذر إلى مسار بايثون للتعرف على الموديولات عند النشر
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# الآن يتم الاستدراك بشكل صحيح بدون خطأ ModuleNotFoundError
from backend.data_providers.market_data import USMarketDataProvider # أو MarketDataProvider حسب مسمى الكلاس لديك
from backend.analysis.technical import TechnicalAnalyzer

class SmartScanner:
    def __init__(self, symbols: List[str]):
        self.symbols = symbols

    def scan_market(self, min_rsi: float = 0, max_rsi: float = 100, trend_filter: str = "الكل") -> List[Dict]:
        results = []
        for sym in self.symbols:
            provider = USMarketDataProvider(sym)
            df = provider.get_history(period="6mo")
            if df.empty:
                continue

            analyzer = TechnicalAnalyzer(df)
            analysis = analyzer.analyze_trend()

            rsi = analysis.get("rsi_value", 50)
            trend = analysis.get("trend", "")

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
