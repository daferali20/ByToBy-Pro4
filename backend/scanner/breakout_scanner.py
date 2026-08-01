import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

@dataclass
class BreakoutIndicators:
    """تخزين مؤشرات الانفجار"""
    is_squeeze: bool
    bandwidth: float
    bandwidth_change: float
    unusual_volume: bool
    volume_ratio: float
    rsi: float
    near_high: bool
    price_position: float  # النسبة المئوية من أعلى سعر
    score: float  # درجة الجاهزية الإجمالية


class BreakoutScanner:
    """
    ماسح الانفجار السعري المتقدم
    يقوم بتحليل شروط الانفجار وفق معايير متعددة
    """
    
    def __init__(self, 
                 squeeze_threshold: float = 1.20,
                 volume_threshold: float = 2.0,
                 rsi_min: float = 45,
                 rsi_max: float = 75,
                 near_high_threshold: float = 0.88,
                 lookback_days: int = 252):
        """
        Args:
            squeeze_threshold: عتبة الانضغاط (كلما قلت كانت أدق)
            volume_threshold: مضاعف الحجم غير الطبيعي
            rsi_min: الحد الأدنى لـ RSI
            rsi_max: الحد الأقصى لـ RSI
            near_high_threshold: نسبة القرب من أعلى سعر
            lookback_days: فترة النظر للخلف
        """
        self.squeeze_threshold = squeeze_threshold
        self.volume_threshold = volume_threshold
        self.rsi_min = rsi_min
        self.rsi_max = rsi_max
        self.near_high_threshold = near_high_threshold
        self.lookback_days = lookback_days
        
    def analyze(self, df: pd.DataFrame) -> Tuple[bool, Optional[BreakoutIndicators]]:
        """
        تحليل شامل للانفجار السعري
        
        Returns:
            (is_breakout, indicators)
        """
        # التحقق من صحة البيانات
        if not self._validate_data(df):
            return False, None
        
        try:
            # حساب جميع المؤشرات
            indicators = self._calculate_indicators(df)
            
            if indicators is None:
                return False, None
            
            # تقييم الشروط
            is_breakout = all([
                indicators.is_squeeze,
                indicators.unusual_volume,
                indicators.rsi_min <= indicators.rsi <= indicators.rsi_max,
                indicators.near_high
            ])
            
            # حساب درجة الجاهزية
            indicators.score = self._calculate_score(indicators)
            
            return is_breakout, indicators
            
        except Exception as e:
            print(f"⚠️ خطأ في تحليل الانفجار: {e}")
            return False, None
    
    def _validate_data(self, df: pd.DataFrame) -> bool:
        """التحقق من صحة البيانات"""
        if df is None or len(df) < 50:
            return False
        
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_cols):
            return False
        
        return True
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Optional[BreakoutIndicators]:
        """حساب جميع المؤشرات الفنية"""
        close = df['Close']
        high = df['High']
        volume = df['Volume']
        
        # 1. حساب Bollinger Bands
        sma_20 = close.rolling(window=20).mean()
        std_20 = close.rolling(window=20).std()
        
        bb_upper = sma_20 + (std_20 * 2)
        bb_lower = sma_20 - (std_20 * 2)
        band_width = (bb_upper - bb_lower) / sma_20
        
        # تجنب القيم NaN
        if band_width.iloc[-1] is None or band_width.iloc[-51:-1].min() is None:
            return None
        
        current_bandwidth = band_width.iloc[-1]
        min_bandwidth_prev = band_width.iloc[-51:-1].min()
        
        # 2. حالة الانضغاط مع تحسين الحساسية
        is_squeeze = current_bandwidth <= (min_bandwidth_prev * self.squeeze_threshold)
        bandwidth_change = ((current_bandwidth - min_bandwidth_prev) / min_bandwidth_prev * 100) if min_bandwidth_prev > 0 else 0
        
        # 3. حجم التداول غير الطبيعي
        avg_volume_20 = volume.iloc[-21:-1].mean()
        current_volume = volume.iloc[-1]
        
        if avg_volume_20 > 0:
            volume_ratio = current_volume / avg_volume_20
            unusual_volume = volume_ratio >= self.volume_threshold
        else:
            volume_ratio = 0
            unusual_volume = False
        
        # 4. حساب RSI مع تحسين الدقة
        rsi = self._calculate_rsi(close)
        if rsi is None:
            return None
        
        # 5. القرب من أعلى سعر
        high_period = high.iloc[-self.lookback_days:].max()
        current_price = close.iloc[-1]
        
        if high_period > 0:
            price_position = current_price / high_period
            near_high = price_position >= self.near_high_threshold
        else:
            price_position = 0
            near_high = False
        
        return BreakoutIndicators(
            is_squeeze=is_squeeze,
            bandwidth=round(current_bandwidth, 4),
            bandwidth_change=round(bandwidth_change, 2),
            unusual_volume=unusual_volume,
            volume_ratio=round(volume_ratio, 2),
            rsi=round(rsi, 2),
            near_high=near_high,
            price_position=round(price_position * 100, 2),
            score=0.0  # سيتم حسابه لاحقاً
        )
    
    def _calculate_rsi(self, close: pd.Series, period: int = 14) -> Optional[float]:
        """حساب RSI يدوياً"""
        try:
            delta = close.diff()
            gain = delta.where(delta > 0, 0.0).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0.0)).rolling(window=period).mean()
            
            # تجنب القسمة على صفر
            loss = loss.replace(0, np.nan)
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            last_rsi = rsi.iloc[-1]
            return float(last_rsi) if not pd.isna(last_rsi) else None
            
        except Exception as e:
            print(f"⚠️ خطأ في حساب RSI: {e}")
            return None
    
    def _calculate_score(self, indicators: BreakoutIndicators) -> float:
        """
        حساب درجة الجاهزية للانفجار (0-100)
        بناءً على وزن المؤشرات المختلفة
        """
        score = 0.0
        
        # 1. درجة الانضغاط (وزن 30%)
        if indicators.is_squeeze:
            # كلما كان الانضغاط أعمق، كلما كانت الدرجة أعلى
            squeeze_strength = min(100, (1 / indicators.bandwidth) * 10) if indicators.bandwidth > 0 else 0
            score += squeeze_strength * 0.30
        
        # 2. درجة حجم التداول (وزن 25%)
        volume_score = min(100, indicators.volume_ratio * 30) if indicators.volume_ratio > 0 else 0
        score += volume_score * 0.25
        
        # 3. درجة RSI (وزن 20%)
        # RSI مثالي بين 50-60 للانفجار الصاعد
        if indicators.rsi is not None:
            if 50 <= indicators.rsi <= 60:
                rsi_score = 100
            elif 45 <= indicators.rsi < 50:
                rsi_score = 70
            elif 60 < indicators.rsi <= 70:
                rsi_score = 80
            elif 70 < indicators.rsi <= 75:
                rsi_score = 60
            else:
                rsi_score = max(0, 100 - abs(indicators.rsi - 55) * 2)
            score += rsi_score * 0.20
        
        # 4. درجة القرب من القمة (وزن 15%)
        price_score = indicators.price_position * 100 if indicators.price_position > 0 else 0
        score += price_score * 0.15
        
        # 5. درجة اتجاه الانضغاط (وزن 10%)
        if indicators.bandwidth_change < 0:
            # الانضغاط يزداد (مؤشر إيجابي)
            trend_score = min(100, abs(indicators.bandwidth_change) * 2)
        else:
            # الانضغاط يخف (مؤشر سلبي)
            trend_score = max(0, 100 - indicators.bandwidth_change * 2)
        score += trend_score * 0.10
        
        # تقريب الدرجة
        return round(min(100, score), 2)


def scan_for_potential_breakouts(df: pd.DataFrame) -> bool:
    """
    دالة متوافقة مع الكود السابق للاستمرارية
    """
    scanner = BreakoutScanner()
    is_breakout, _ = scanner.analyze(df)
    return is_breakout


def scan_with_details(df: pd.DataFrame) -> Dict[str, Any]:
    """
    مسح مفصل مع عرض جميع المؤشرات
    """
    scanner = BreakoutScanner()
    is_breakout, indicators = scanner.analyze(df)
    
    if indicators is None:
        return {
            'is_breakout': False,
            'error': 'فشل في تحليل البيانات'
        }
    
    return {
        'is_breakout': is_breakout,
        'score': indicators.score,
        'details': {
            'squeeze': {
                'status': '✅' if indicators.is_squeeze else '❌',
                'bandwidth': indicators.bandwidth,
                'change': f"{indicators.bandwidth_change:.1f}%"
            },
            'volume': {
                'unusual': '✅' if indicators.unusual_volume else '❌',
                'ratio': f"{indicators.volume_ratio:.2f}x"
            },
            'rsi': {
                'value': indicators.rsi,
                'status': 'مناسب' if 45 <= indicators.rsi <= 75 else 'خارج النطاق'
            },
            'price': {
                'near_high': '✅' if indicators.near_high else '❌',
                'position': f"{indicators.price_position:.1f}% من القمة"
            }
        }
    }


def scan_multiple_stocks(stock_data: Dict[str, pd.DataFrame], 
                         min_score: float = 70) -> pd.DataFrame:
    """
    مسح عدة أسهم وعرض النتائج كجدول
    
    Args:
        stock_data: قاموس {symbol: dataframe}
        min_score: الحد الأدنى للدرجة المطلوبة
    
    Returns:
        DataFrame بالنتائج
    """
    scanner = BreakoutScanner()
    results = []
    
    for symbol, df in stock_data.items():
        is_breakout, indicators = scanner.analyze(df)
        
        if indicators is not None and is_breakout and indicators.score >= min_score:
            results.append({
                'Symbol': symbol,
                'Score': indicators.score,
                'Squeeze': '✅' if indicators.is_squeeze else '❌',
                'Volume Ratio': f"{indicators.volume_ratio:.1f}x",
                'RSI': indicators.rsi,
                'Price Position': f"{indicators.price_position:.1f}%",
                'Bandwidth': f"{indicators.bandwidth:.3f}"
            })
    
    if results:
        return pd.DataFrame(results).sort_values('Score', ascending=False)
    return pd.DataFrame()


# مثال للاستخدام
def demo():
    """مثال توضيحي لاستخدام الماسح"""
    # إنشاء بيانات تجريبية
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    data = {
        'Open': np.random.randn(100).cumsum() + 100,
        'High': np.random.randn(100).cumsum() + 102,
        'Low': np.random.randn(100).cumsum() + 98,
        'Close': np.random.randn(100).cumsum() + 100,
        'Volume': np.random.randint(1000000, 10000000, 100)
    }
    df = pd.DataFrame(data, index=dates)
    
    # إضافة بعض الشروط المحاكية للانفجار
    df.loc[df.index[-1], 'Close'] = df['Close'].iloc[-2] * 1.05  # ارتفاع 5%
    df.loc[df.index[-1], 'Volume'] = df['Volume'].iloc[-2] * 3   # حجم 3 أضعاف
    
    # التحليل
    result = scan_with_details(df)
    
    print("📊 نتائج التحليل:")
    print(f"هل هو انفجار سعري؟ {'✅' if result['is_breakout'] else '❌'}")
    print(f"درجة الجاهزية: {result['score']}/100")
    print("\nالتفاصيل:")
    for key, value in result['details'].items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    demo()
