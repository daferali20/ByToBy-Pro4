from backend.data_providers.market_data import MarketDataProvider
from backend.analysis.technical import TechnicalAnalyzer
from backend.pattern_detection.patterns import PatternDetector

class StockService:
    @staticmethod
    def get_full_analysis(symbol: str) -> dict:
        """توفير تقرير شامل وموحد للسهم"""
        provider = MarketDataProvider(symbol)
        df = provider.get_history(period="1y")
        
        if df.empty:
            return {"error": f"لا توجد بيانات متاحة للسهم {symbol}"}

        tech_analyzer = TechnicalAnalyzer(df)
        tech_summary = tech_analyzer.analyze_trend()

        pattern_detector = PatternDetector(df)
        patterns = {
            "bullish_engulfing": pattern_detector.detect_bullish_engulfing(),
            "breakout_20d": pattern_detector.detect_breakout(lookback=20)
        }

        info = provider.get_info()

        return {
            "symbol": symbol,
            "company_name": info.get("longName", symbol),
            "current_price": tech_summary.get("last_close"),
            "technical_summary": tech_summary,
            "patterns": patterns,
            "raw_data": df
        }
