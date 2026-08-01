# backend/scanner/screener.py

import sys
import os
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. إضافة المجلد الرئيسي للمشروع بشكل صحيح
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# 2. استيراد الموديولات الداخلية لـ Backend
try:
    from backend.data_providers.market_data import USMarketDataProvider 
    from backend.analysis.technical import TechnicalAnalyzer
    from backend.scanner.breakout_scanner import scan_for_potential_breakouts, get_breakout_candidates
except ImportError as e:
    logger.error(f"⚠️ فشل في استيراد الوحدات الداخلية لـ Backend: {e}")
    raise

# 3. استخدام DataClass للنتائج
@dataclass
class ScanResult:
    symbol: str
    close: float
    rsi: float
    trend: str
    macd_signal: str
    scan_time: datetime = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "close": self.close,
            "rsi": self.rsi,
            "trend": self.trend,
            "macd_signal": self.macd_signal,
            "scan_time": self.scan_time.isoformat()
        }


class SmartScanner:
    """الماسح الذكي للأسهم - يقوم بتحليل الأسهم وتصفيتها وفق معايير محددة"""
    
    def __init__(self, symbols: List[str], cache_duration: int = 300):
        """
        Args:
            symbols: قائمة رموز الأسهم
            cache_duration: مدة صلاحية الكاش بالثواني (افتراضي 5 دقائق)
        """
        self.symbols = symbols
        self.cache_duration = cache_duration
        self._cache = {}  # تخزين مؤقت للنتائج
        self._last_scan = None

    def _is_cache_valid(self) -> bool:
        """التحقق من صلاحية الكاش"""
        if self._last_scan is None:
            return False
        elapsed = (datetime.now() - self._last_scan).total_seconds()
        return elapsed < self.cache_duration

    def _analyze_symbol(self, symbol: str) -> Optional[ScanResult]:
        """تحليل سهم فردي مع معالجة الأخطاء"""
        try:
            # 1. جلب البيانات
            provider = USMarketDataProvider(symbol)
            df = provider.get_history(period="6mo")
            
            if df is None or df.empty or len(df) < 20:
                logger.warning(f"⚠️ بيانات غير كافية للسهم {symbol}")
                return None

            # 2. إجراء التحليل الفني
            analyzer = TechnicalAnalyzer(df)
            analysis = analyzer.analyze_trend()

            if not analysis or not isinstance(analysis, dict):
                logger.warning(f"⚠️ تحليل فاشل للسهم {symbol}")
                return None

            # 3. استخراج النتائج بشكل آمن
            rsi = float(analysis.get("rsi_value", 50.0))
            trend = str(analysis.get("trend", "غير معروف"))
            last_close = analysis.get("last_close", 
                                     df['Close'].iloc[-1] if 'Close' in df else 0.0)
            macd_signal = str(analysis.get("macd_signal", "محايد"))

            return ScanResult(
                symbol=symbol,
                close=round(float(last_close), 2),
                rsi=round(rsi, 2),
                trend=trend,
                macd_signal=macd_signal
            )
            
        except Exception as e:
            logger.error(f"⚠️ تعذر تحليل السهم {symbol}: {e}")
            return None

    def scan_market(self, min_rsi: float = 0, max_rsi: float = 100, 
                   trend_filter: str = "الكل", use_cache: bool = True) -> List[Dict]:
        """
        مسح السوق وتصفية الأسهم حسب المعايير
        
        Args:
            min_rsi: الحد الأدنى لـ RSI
            max_rsi: الحد الأقصى لـ RSI
            trend_filter: "الكل" أو "صاعد" أو "هابط" أو "جانبي"
            use_cache: استخدام النتائج المخزنة مؤقتاً
        
        Returns:
            قائمة بالنتائج كقاموس
        """
        # استخدام الكاش إذا كان متاحاً وصالحاً
        if use_cache and self._is_cache_valid():
            logger.info("📦 استخدام النتائج المخزنة مؤقتاً")
            return self._cache

        logger.info(f"🔍 بدء مسح {len(self.symbols)} سهماً...")
        results = []

        for sym in self.symbols:
            result = self._analyze_symbol(sym)
            if result is None:
                continue

            # تطبيق شروط الفلترة
            if min_rsi <= result.rsi <= max_rsi:
                if trend_filter == "الكل" or (trend_filter in result.trend):
                    results.append(result.to_dict())

        logger.info(f"✅ اكتمل المسح: تم العثور على {len(results)} سهماً مطابقة")
        
        # تحديث الكاش
        self._cache = results
        self._last_scan = datetime.now()
        
        return results

    def get_summary(self, results: List[Dict]) -> Dict:
        """الحصول على ملخص للنتائج"""
        if not results:
            return {"count": 0, "avg_rsi": 0, "trends": {}}
        
        rsi_values = [r["rsi"] for r in results]
        trends = {}
        for r in results:
            trend = r.get("trend", "غير معروف")
            trends[trend] = trends.get(trend, 0) + 1
        
        return {
            "count": len(results),
            "avg_rsi": round(sum(rsi_values) / len(rsi_values), 2),
            "min_rsi": min(rsi_values),
            "max_rsi": max(rsi_values),
            "trends": trends,
            "scan_time": datetime.now().isoformat()
        }


# استخدام مبسط
def quick_scan(symbols: List[str], min_rsi: int = 50, max_rsi: int = 70) -> List[Dict]:
    """دالة سريعة للمسح بمعايير افتراضية"""
    scanner = SmartScanner(symbols)
    return scanner.scan_market(min_rsi=min_rsi, max_rsi=max_rsi, trend_filter="صاعد")
