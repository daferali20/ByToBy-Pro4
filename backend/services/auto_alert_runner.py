# backend/services/auto_alert_runner.py

import os
import sys

# ضمان التعرف على مجلد Root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import yfinance as yf
from backend.services.notifier import AlertNotifier

# قائمة الأسهم والمستويات المستهدفة للشراء/البيع أو كسر الدعوم
ALERT_RULES = [
    {
        "symbol": "NVDA",
        "target_price_high": 140.0,  # تنبيه عند التجاوز أعلاه (مقاومة)
        "target_price_low": 115.0,   # تنبيه عند الهبوط أدناه (دعم)
        "rsi_overbought": 75,
    },
    {
        "symbol": "AAPL",
        "target_price_high": 240.0,
        "target_price_low": 210.0,
        "rsi_overbought": 70,
    },
    {
        "symbol": "TSLA",
        "target_price_high": 260.0,
        "target_price_low": 200.0,
        "rsi_overbought": 70,
    }
]

def calculate_rsi(prices, period=14):
    """حساب سريع لمؤشر RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def run_alert_checks():
    # قراءة بيانات الاعتماد من البيئة (Environment Variables)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("❌ لم يتم العثور على TELEGRAM_BOT_TOKEN أو TELEGRAM_CHAT_ID في متغيرات البيئة.")
        return

    notifier = AlertNotifier(bot_token, chat_id)

    print("🔍 بدء فحص أسعار الأسهم ومستويات الكسر...")

    for rule in ALERT_RULES:
        symbol = rule["symbol"]
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1mo")

            if df.empty:
                continue

            current_price = df['Close'].iloc[-1]
            rsi_series = calculate_rsi(df['Close'])
            current_rsi = rsi_series.iloc[-1]

            alerts_to_send = []

            # 1. فحص كسر مستوى المقاومة (سعر أعلى)
            if "target_price_high" in rule and current_price >= rule["target_price_high"]:
                alerts_to_send.append(
                    f"🚀 **تجاوز مستوى المقاومة!**\nالسعر الحالي `${current_price:.2f}` تخطى الهدف `${rule['target_price_high']}`"
                )

            # 2. فحص كسر مستوى الدعم (سعر أدنى)
            if "target_price_low" in rule and current_price <= rule["target_price_low"]:
                alerts_to_send.append(
                    f"⚠️ **كسر مستوى الدعم!**\nالسعر الحالي `${current_price:.2f}` نزل عن `${rule['target_price_low']}`"
                )

            # 3. فحص تشبع الشراء RSI
            if "rsi_overbought" in rule and current_rsi >= rule["rsi_overbought"]:
                alerts_to_send.append(
                    f"📊 **تشبع شرائي مرتفع (RSI)!**\nمؤشر القوة النسبية وصل إلى `{current_rsi:.1f}`"
                )

            # إرسال التنبيهات عبر تلجرام إذا تحققت الشروط
            for alert_msg in alerts_to_send:
                full_message = f"🔔 *تنبيه آلي للسهم: {symbol}*\n\n{alert_msg}\n\n⏱️ _ByToBy-Pro4 Auto Worker_"
                notifier.send_telegram_alert(full_message)
                print(f"✅ تم إرسال تنبيه لـ {symbol}")

        except Exception as e:
            print(f"❌ خطأ أثناء معالجة {symbol}: {e}")

if __name__ == "__main__":
    run_alert_checks()
