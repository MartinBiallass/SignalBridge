import json
from datetime import datetime

# Test: Multi-Trade Speicherung in trades.json

def load_trades():
    try:
        with open("trades.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_trades(trades):
    with open("trades.json", "w") as file:
        json.dump(trades, file, indent=4)

# Beispiel-Signal mit mehreren Trades
multi_trade_signal = {
    "signal_id": "FX12345",
    "symbol": "EURUSD",
    "trades": [
        {"entry_point": 1.1200, "stop_loss": 1.1150, "take_profit": 1.1250, "lot_size": 0.1},
        {"entry_point": 1.1210, "stop_loss": 1.1160, "take_profit": 1.1260, "lot_size": 0.2},
        {"entry_point": 1.1220, "stop_loss": 1.1170, "take_profit": 1.1270, "lot_size": 0.15}
    ],
    "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
}

# Laden bestehender Trades
existing_trades = load_trades()

# Trade speichern
existing_trades[multi_trade_signal["signal_id"]] = multi_trade_signal
save_trades(existing_trades)

print("✅ Multi-Trade gespeichert:", json.dumps(multi_trade_signal, indent=4))

