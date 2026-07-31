from typing import List, Dict

class AlertManager:
    def __init__(self):
        self.alerts: List[Dict] = []

    def add_alert(self, symbol: str, target_price: float, condition: str) -> Dict:
        alert = {
            "id": len(self.alerts) + 1,
            "symbol": symbol,
            "target_price": target_price,
            "condition": condition, # 'ABOVE' or 'BELOW'
            "status": "Active 🟢"
        }
        self.alerts.append(alert)
        return alert

    def check_alerts(self, current_prices: Dict[str, float]) -> List[str]:
        triggered = []
        for alert in self.alerts:
            sym = alert["symbol"]
            if sym in current_prices and alert["status"] == "Active 🟢":
                curr_price = current_prices[sym]
                if alert["condition"] == "ABOVE" and curr_price >= alert["target_price"]:
                    alert["status"] = "Triggered 🔔"
                    triggered.append(f"تنبيه: السهم {sym} تجاوز السعر المستهدف {alert['target_price']} (السعر الحالي: {curr_price})")
                elif alert["condition"] == "BELOW" and curr_price <= alert["target_price"]:
                    alert["status"] = "Triggered 🔔"
                    triggered.append(f"تنبيه: السهم {sym} انخفض عن السعر المستهدف {alert['target_price']} (السعر الحالي: {curr_price})")
        return triggered
