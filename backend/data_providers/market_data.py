# backend/data_providers/market_data.py

import pandas as pd
import yfinance as yf
from backend.utils import calculate_technical_indicators

class USMarketDataProvider:
    def __init__(self, symbol: str):
        # تحويل الرمز إلى حروف كبيرة للتأكد من الملاءمة مع بورصات أمريكا
        self.symbol = symbol.upper().strip()
        self.ticker = yf.Ticker(self.symbol)

    def get_realtime_price(self) -> dict:
        """جلب السعر الحي والتغير اليومي للأسهم الأمريكية"""
        try:
            fast_info = self.ticker.fast_info
            last_price = fast_info.last_price
            prev_close = fast_info.previous_close
            change = last_price - prev_close
            change_pct = (change / prev_close) * 100

            return {
                "symbol": self.symbol,
                "current_price": round(last_price, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "previous_close": round(prev_close, 2)
            }
        except Exception as e:
            return {"error": f"Failed to fetch live price for {self.symbol}: {e}"}

    def get_history(self, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """جلب البيانات التاريخية من البورصات الأمريكية مع المؤشرات الفنية"""
        try:
            df = self.ticker.history(period=period, interval=interval)
            if df.empty:
                return pd.DataFrame()
            
            # حساب المؤشرات الفنية (RSI, SMA, MACD, etc.)
            df = calculate_technical_indicators(df)
            return df
        except Exception as e:
            print(f"Error fetching history for {self.symbol}: {e}")
            return pd.DataFrame()

    def get_company_fundamentals(self) -> dict:
        """جلب البيانات الأساسية الحقيقية (المالية، مكرر الربحية، ربحية السهم)"""
        try:
            info = self.ticker.info
            return {
                "company_name": info.get("longName", self.symbol),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0.0),
                "forward_pe": info.get("forwardPE", 0.0),
                "eps": info.get("trailingEps", 0.0),
                "dividend_yield": info.get("dividendYield", 0.0) * 100 if info.get("dividendYield") else 0.0,
                "target_high_price": info.get("targetHighPrice", 0.0),
                "52_week_high": info.get("fiftyTwoWeekHigh", 0.0),
                "52_week_low": info.get("fiftyTwoWeekLow", 0.0)
            }
        except Exception as e:
            return {"error": f"Error loading fundamentals for {self.symbol}: {e}"}
