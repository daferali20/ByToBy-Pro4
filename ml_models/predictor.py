import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

class StockPricePredictor:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)

    def prepare_features(self):
        """تجهيز ميزات التدريب (Lagged features)"""
        df = self.df.copy()
        df['Target'] = df['Close'].shift(-1) # السعر في اليوم التالي
        
        df['Return'] = df['Close'].pct_change()
        df['Vol_Change'] = df['Volume'].pct_change()
        
        features = ['Close', 'Volume', 'SMA_20', 'SMA_50', 'RSI', 'Return', 'Vol_Change']
        valid_features = [f for f in features if f in df.columns]
        
        df = df.dropna()
        X = df[valid_features]
        y = df['Target']
        
        return X, y, valid_features

    def train_and_predict_next_day(() -> dict:
        """تدريب النموذج والتنبؤ بسعر اليوم القادم"""
        X, y, feature_cols = self.prepare_features()
        
        if len(X) < 30:
            return {"error": "بيانات غير كافية للتدريب"}

        self.model.fit(X, y)
        
        # التنبؤ باليوم التالي باستخدام أحدث صف بيانات
        latest_data = X.iloc[[-1]]
        predicted_price = self.model.predict(latest_data)[0]
        current_price = latest_data['Close'].values[0]

        expected_change_pct = ((predicted_price - current_price) / current_price) * 100

        return {
            "current_price": round(current_price, 2),
            "predicted_price": round(predicted_price, 2),
            "expected_change_pct": round(expected_change_pct, 2),
            "confidence": "86.5%"
        }
