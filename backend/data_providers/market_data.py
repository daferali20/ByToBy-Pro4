import pandas as pd
import yfinance as yf
from backend.utils import calculate_technical_indicators


class MarketDataProvider:

  def __init__(self, symbol: str):
    self.symbol = symbol
    self.ticker = yf.Ticker(symbol)

  def get_history(
      self, period: str = '1y', interval: str = '1d'
  ) -> pd.DataFrame:
    """جلب البيانات التاريخية وحساب المؤشرات الفنية"""
    try:
      df = self.ticker.history(period=period, interval=interval)
      if df.empty:
        return pd.DataFrame()
      df = calculate_technical_indicators(df)
      return df
    except Exception as e:
      print(f'Error fetching data for {self.symbol}: {e}')
      return pd.DataFrame()

  def get_info(self) -> dict:
    """جلب معلومات السهم والبيانات الأساسية"""
    try:
      return self.ticker.info
    except Exception as e:
      return {'error': str(e)}
