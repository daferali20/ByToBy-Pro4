from backend.news.sentiment_analyst import NewsSentimentAnalyst

class MarketSentimentModel:
    def __init__(self):
        self.analyst = NewsSentimentAnalyst()

    def aggregate_news_sentiment(self, news_articles: list) -> dict:
        """تحليل التوجه العام لمجموعة من الأخبار"""
        if not news_articles:
            return {"overall_sentiment": "محايد ⚪", "avg_score": 0.0}

        total_score = 0.0
        results = []

        for article in news_articles:
            res = self.analyst.analyze_text(article)
            results.append(res)
            total_score += res["score"]

        avg_score = total_score / len(news_articles)

        if avg_score > 0.2:
            overall = "إيجابي جداً 🚀"
        elif avg_score > 0.0:
            overall = "إيجابي 🟢"
        elif avg_score < -0.2:
            overall = "سلبي جداً 🔻"
        elif avg_score < 0.0:
            overall = "سلبي 🔴"
        else:
            overall = "محايد ⚪"

        return {
            "overall_sentiment": overall,
            "average_score": round(avg_score, 2),
            "total_articles_analyzed": len(news_articles)
        }
