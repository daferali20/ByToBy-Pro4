# ml_models/recommendation.py

import os
import sys

# ضمان التعرف على مجلد Root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from ml_models.stock_rating import StockRatingEngine
from ml_models.fair_value import FairValueCalculator


class RecommendationEngine:

  @staticmethod
  def get_final_recommendation(
      symbol: str,
      current_price: float,
      rsi: float,
      pe: float,
      margin: float,
      eps: float,
      growth: float,
      trend: str,
  ) -> dict:
    """توليد توصية استثمارية نهائية"""

    # 1. Rating Engine
    rater = StockRatingEngine(rsi, pe, margin, trend)
    rating = rater.generate_rating()

    # 2. Fair Value Engine
    fv_calc = FairValueCalculator(eps, growth, pe if pe and pe > 0 else 15)
    valuation = fv_calc.evaluate_valuation(current_price)

    return {
        "symbol": symbol,
        "score": rating["overall_score"],
        "rating": rating["rating_label"],
        "fair_value": valuation["fair_value"],
        "valuation_status": valuation["status"],
        "action_summary": (
            f"بناءً على تقييم {rating['overall_score']}/100 والقيمة العادلة"
            f" ${valuation['fair_value']}، النتيجة: {rating['rating_label']}"
        ),
    }
