# backend/config.py

# قائمة الأسهم الأمريكية الأكثر تداولاً (S&P 500 / NASDAQ Highlights)
US_STOCK_WATCHLIST = [
    "AAPL",  # Apple
    "MSFT",  # Microsoft
    "NVDA",  # Nvidia
    "GOOGL", # Alphabet (Google)
    "AMZN",  # Amazon
    "META",  # Meta (Facebook)
    "TSLA",  # Tesla
    "AMD",   # Advanced Micro Devices
    "NFLX",  # Netflix
    "INTC",  # Intel
    "JPM",   # JPMorgan Chase
    "V",     # Visa
    "WMT",   # Walmart
    "BAC",   # Bank of America
    "PG"     # Procter & Gamble
]

# المؤشرات الأمريكية المرجعية
US_MARKET_INDEXES = {
    "S&P 500": "^GSPC",
    "Nasdaq 100": "^IXIC",
    "Dow Jones": "^DJI",
    "Volatility Index (VIX)": "^VIX"
}
