# backend/scanner/screener.py

import sys
import os
from typing import List, Dict

# إضافة مجلد الجذر إلى مسار بايثون للتعرف على الموديولات عند النشر
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# استيراد الوظائف المطلوبة من backend
try:
    from backend.data_providers.market_data import USMarketDataProvider 
    from backend.analysis.technical import TechnicalAnalyzer
except ImportError as e:
    # حماية ضد أخطاء الاستيراد أثناء التطوير
    raise ImportError(f"فشل في استيراد الوحدات الخاصة بـ Backend: {e}")

class SmartScanner:
    def __init__(self, symbols: List[str]):
        self.symbols = symbols

    def scan_market(self, min_rsi: float = 0, max_rsi: float = 100, trend_filter: str = "الكل") -> List[Dict]:
        results = []
        
        for sym in self.symbols:
            try:
                # 1. جلب البيانات بحماية
                provider = USMarketDataProvider(sym)
                df = provider.get_history(period="6mo")
                
                if df is None or df.empty or len(df) < 20:
                    continue

                # 2. إجراء التحليل الفني
                analyzer = TechnicalAnalyzer(df)
                analysis = analyzer.analyze_trend()

                if not analysis or not isinstance(analysis, dict):
                    continue

                # 3. قراءة المخرجات بشكل آمن باستخدام .get() مع وضع قيم افتراضية
                rsi = float(analysis.get("rsi_value", 50.0))
                trend = str(analysis.get("trend", ""))
                last_close = analysis.get("last_close", df['Close'].iloc[-1] if 'Close' in df else 0.0)
                macd_signal = analysis.get("macd_signal", "محايد")

                # 4. تطبيق شروط الفلترة
                if min_rsi <= rsi <= max_rsi:
                    if trend_filter == "الكل" or (trend_filter in trend):
                        results.append({
                            "symbol": sym,
                            "close": round(float(last_close), 2),
                            "rsi": round(rsi, 2),
                            "trend": trend,
                            "macd_signal": macd_signal
                        })
                        
            except Exception as e:
                # في حال تعثر جلب بيانات سهم معين، يتخطاه ويستكمل باقي القائمة
                print(f"⚠️ تعذر تحليل السهم {sym}: {e}")
                continue
                
        return results
