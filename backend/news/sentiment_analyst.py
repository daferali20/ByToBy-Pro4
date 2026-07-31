class NewsSentimentAnalyst:
    def __init__(self):
        pass

    def analyze_text(self, text: str) -> dict:
        """تحليل النص المالي وتحديد الشعور (إيجابي / سلبي / محايد)"""
        text_lower = text.lower()
        
        positive_keywords = ["أرباح", "ارتفاع", "نمو", "توزيعات", "توسع", "عقد", "تجاوز", "profit", "growth", "surge", "gain"]
        negative_keywords = ["خسارة", "انخفاض", "تراجع", "دعوى", "انكماش", "ديون", "loss", "decline", "drop", "debt"]

        pos_score = sum(1 for word in positive_keywords if word in text_lower)
        neg_score = sum(1 for word in negative_keywords if word in text_lower)

        if pos_score > neg_score:
            sentiment = "إيجابي 🟢"
            score = 0.75
        elif neg_score > pos_score:
            sentiment = "سلبي 🔴"
            score = -0.75
        else:
            sentiment = "محايد ⚪"
            score = 0.0

        return {
            "text_snippet": text[:60] + "...",
            "sentiment": sentiment,
            "score": score
        }
