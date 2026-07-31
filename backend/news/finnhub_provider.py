import requests
from datetime import datetime, timedelta

class FinnhubUSNews:
    def __init__(self, api_key: str = "d4t60ipr01qhr5tofrb0d4t60ipr01qhr5tofrbg"):
        self.api_key = api_key
        self.base_url = "https://finnhub.io/api/v1"

    def get_company_news(self, symbol: str) -> list:
        """جلب أخبار السهم من Finnhub"""
        today = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        url = f"{self.base_url}/company-news?symbol={symbol.upper()}&from={from_date}&to={today}&token={self.api_key}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        return []
