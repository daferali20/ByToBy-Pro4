import numpy as np
import pandas as pd

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """حساب المؤشرات الفنية الأساسية (RSI, SMA, EMA, MACD, Bollinger Bands)"""
    if df.empty or len(df) < 14:
        return df

    # Simple Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()

    # Exponential Moving Average
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()

    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # RSI (Relative Strength Index)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))

    # Bollinger Bands
    df['BB_Middle'] = df['SMA_20']
    std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (std * 2)

    return df

def format_currency(val: float, currency: str = "SAR") -> str:
    """تنسيق الأرقام كعملة"""
    return f"{val:,.2f} {currency}"
