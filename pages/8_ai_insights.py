import streamlit as st
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.data_providers.market_data import MarketDataProvider
from ml_models.predictor import StockPricePredictor
from ml_models.recommendation import RecommendationEngine

st.title("🤖 التنبؤ والتوصيات بالذكاء الاصطناعي")

symbol = st.selectbox("اختر السهم للتحليل التنبؤي:", ["2222.SR", "1120.SR", "AAPL"])

if st.button("تشغيل خوارزمية الذكاء الاصطناعي"):
    with st.spinner("جاري تدريب النموذج وقراءة المعطيات..."):
        # 1. جلب البيانات
        provider = MarketDataProvider(symbol)
        df = provider.get_history(period="1y")

        if df.empty:
            st.error("تعذر جلب البيانات لتشغيل النموذج.")
        else:
            # 2. تشغيل نموذج التنبؤ بسعر الغد
            predictor = StockPricePredictor(df)
            pred_results = predictor.train_and_predict_next_day()

            if "error" in pred_results:
                st.warning(pred_results["error"])
            else:
                st.success("تم تشغيل النموذج بنجاح!")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("السعر الحالي", f"{pred_results['current_price']} SAR")
                c2.metric("السعر المتوقع (غداً)", f"{pred_results['predicted_price']} SAR", delta=f"{pred_results['expected_change_pct']}%")
                c3.metric("نسبة الثقة", pred_results["confidence"])

            # 3. تشغيل محرك التوصيات النهائي
            rec = RecommendationEngine.get_final_recommendation(
                symbol=symbol,
                current_price=df['Close'].iloc[-1],
                rsi=df['RSI'].iloc[-1] if 'RSI' in df.columns else 50,
                pe=18.5, # قيمة افتراضية أو مستخرجة من info
                margin=0.20,
                eps=2.5,
                growth=0.08,
                trend="صاعد"
            )

            st.divider()
            st.subheader("🎯 التوصية النهائية للنظام:")
            st.info(rec["action_summary"])
            
            val_col1, val_col2 = st.columns(2)
            val_col1.metric("النتيجة الإجمالية (Score)", f"{rec['score']}/100")
            val_col2.metric("القيمة العادلة المتوقعة", f"{rec['fair_value']} SAR", delta=rec["valuation_status"])
