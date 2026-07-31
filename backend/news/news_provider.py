# backend/news/news_provider.py

import yfinance as yf
from datetime import datetime
from backend.news.sentiment_analyst import NewsSentimentAnalyst

class USNewsProvider:
    def __init__(self):
        self.analyst = NewsSentimentAnalyst()

    def get_stock_news(self, symbol: str, limit: int = 5) -> list:
        """جلب الأخبار الحية لسهم أمريكي محدد"""
        symbol = symbol.upper().strip()
        ticker = yf.Ticker(symbol)
        
        try:
            raw_news = ticker.news
            processed_news = []

            for item in raw_news[:limit]:
                title = item.get("title", "")
                publisher = item.get("publisher", "Market News")
                link = item.get("link", "#")
                pub_time = item.get("providerPublishTime", None)

                # تحويل الوقت لتنسيق مفهوم
                formatted_time = (
                    datetime.fromtimestamp(pub_time).strftime('%Y-%m-%d %H:%M')
                    if pub_time else "الحالي"
                )

                # تحليل انطباع الخبر (إيجابي / سلبي / محايد)
                sentiment_res = self.analyst.analyze_text(title)

                processed_news.append({
                    "symbol": symbol,
                    "title": title,
                    "publisher": publisher,
                    "link": link,
                    "published_at": formatted_time,
                    "sentiment": sentiment_res["sentiment"],
                    "sentiment_score": sentiment_res["score"]
                })

            return processed_news
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return []

    def get_market_wide_us_news(self, symbols_list: list, limit_per_stock: int = 2) -> list:
        """جلب تغذية إخبارية شاملة لأسواق الأسهم الأمريكية"""
        all_news = []
        for sym in symbols_list:
            news = self.get_stock_news(sym, limit=limit_per_stock)
            all_news.extend(news)
        
        # ترتيب الأخبار من الأحدث للأقدم
        return sorted(all_news, key=lambda x: x['published_at'], reverse=True)
