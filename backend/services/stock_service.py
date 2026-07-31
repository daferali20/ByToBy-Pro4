# backend/services/stock_service.py

from backend.data_providers.market_data import USMarketDataProvider
from backend.analysis.technical import TechnicalAnalyzer
from backend.pattern_detection.patterns import PatternDetector

class USStockService:
    @staticmethod
    def get_full_stock_report(symbol: str) -> dict:
        """توفير تقرير شامل ومباشر لجميع بيانات السهم الأمريكي"""
        provider = USMarketDataProvider(symbol)
        
        # 1. الأسعار الحية والبيانات الأساسية
        live_price = provider.get_realtime_price()
        fundamentals = provider.get_company_fundamentals()
        
        # 2. السجل التاريخي والتحليل التقني
        df = provider.get_history(period="1y")
        if df.empty:
            return {"error": f"Invalid symbol or no data available for '{symbol}' in US markets."}

        tech_analyzer = TechnicalAnalyzer(df)
        tech_summary = tech_analyzer.analyze_trend()

        pattern_detector = PatternDetector(df)
        patterns = {
            "bullish_engulfing": pattern_detector.detect_bullish_engulfing(),
            "breakout_20d": pattern_detector.detect_breakout(lookback=20)
        }

        return {
            "symbol": symbol.upper(),
            "live": live_price,
            "fundamentals": fundamentals,
            "technical": tech_summary,
            "patterns": patterns,
            "df": df
        }
