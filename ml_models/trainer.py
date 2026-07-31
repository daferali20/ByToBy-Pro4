import os
import joblib
from ml_models.predictor import StockPricePredictor
from backend.data_providers.market_data import MarketDataProvider

MODEL_SAVE_PATH = "ml_models/saved_models/"

def train_and_save_model(symbol: str):
    """تدريب نموذج سهم محدد وحفظه كملف .pkl"""
    print(f"بدء تدريب النموذج للسهم {symbol}...")
    
    provider = MarketDataProvider(symbol)
    df = provider.get_history(period="2y")
    
    if df.empty:
        print("خطأ: لا توجد بيانات كافية.")
        return

    predictor = StockPricePredictor(df)
    X, y, _ = predictor.prepare_features()
    
    predictor.model.fit(X, y)

    os.makedirs(MODEL_SAVE_PATH, exist_ok=True)
    file_path = os.path.join(MODEL_SAVE_PATH, f"{symbol}_model.pkl")
    joblib.dump(predictor.model, file_path)
    
    print(f"تم حفظ النموذج بنجاح في: {file_path}")

if __name__ == "__main__":
    # مثال لتدريب النموذج لسهم أرامكو والراجحي
    train_and_save_model("2222.SR")
    train_and_save_model("1120.SR")
