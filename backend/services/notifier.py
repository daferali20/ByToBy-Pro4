# backend/services/notifier.py

import requests
import smtplib
from email.mime.text import MIMEText

class AlertNotifier:
    def __init__(self, telegram_token: str = None, chat_id: str = None):
        self.telegram_token = telegram_token
        self.chat_id = chat_id

    def send_telegram_alert(self, message: str) -> bool:
        """إرسال تنبيه حقيقي مباشرة لحسابك على Telegram"""
        if not self.telegram_token or not self.chat_id:
            return False
            
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            res = requests.post(url, json=payload, timeout=5)
            return res.status_code == 200
        except Exception as e:
            print(f"Telegram Alert Failed: {e}")
            return False

    def send_email_alert(self, subject: str, body: str, to_email: str, smtp_config: dict) -> bool:
        """إرسال تنبيه عبر البريد الإلكتروني"""
        try:
            msg = MIMEText(body, 'html')
            msg['Subject'] = subject
            msg['From'] = smtp_config['sender_email']
            msg['To'] = to_email

            with smtplib.SMTP_SSL(smtp_config['smtp_server'], smtp_config['smtp_port']) as server:
                server.login(smtp_config['sender_email'], smtp_config['sender_password'])
                server.sendmail(smtp_config['sender_email'], [to_email], msg.as_string())
            return True
        except Exception as e:
            print(f"Email Alert Failed: {e}")
            return False
