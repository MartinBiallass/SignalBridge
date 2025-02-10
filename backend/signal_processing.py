import re
from datetime import datetime
# Importiere den Optionstrading-Manager aus der Datei option_trading.py
from backend.option_trading import OptionTradeManager

# Instanz des Managers erstellen
trade_manager = OptionTradeManager()

# Signal-Parsing-Funktion
def parse_signal(message):
    signal_pattern = r"(Buy|Sell)\s+(\w+)\s+@\s+([\d.]+)(?:,?\s*SL:\s*([\d.]+))?(?:,?\s*TP1:\s*([\d.]+))?(?:,?\s*TP2:\s*([\d.]+))?(?:,?\s*TP3:\s*([\d.]+))?"
    match = re.search(signal_pattern, message, re.IGNORECASE)
    if match:
        return {
            "action": match.group(1),
            "symbol": match.group(2),
            "entry_price": float(match.group(3)),
            "stop_loss": float(match.group(4)) if match.group(4) else None,
            "tp_values": {
                "TP1": float(match.group(5)) if match.group(5) else None,
                "TP2": float(match.group(6)) if match.group(6) else None,
                "TP3": float(match.group(7)) if match.group(7) else None,
            },
            "timestamp": datetime.now().isoformat()
        }
    return None
def process_signal(message):
    signal = parse_signal(message)  # Standard-Signalverarbeitung
    
    if signal:
        print(f"✅ Signal erkannt: {signal}")
        
        # Prüfen, ob das Signal für Optionstrading geeignet ist (ob eine Zeitangabe enthalten ist)
        option_trade_data = trade_manager.parse_signal(message)
        if option_trade_data:  # Falls die Optionstrading-Logik eine gültige Laufzeit erkennt
            trade_id = f"{signal['symbol']}_{datetime.now().strftime('%H%M%S')}"
            trade_manager.open_trade(trade_id, message)

    else:
        print("❌ Kein gültiges Signal erkannt.")


# Testnachrichten
test_messages = [
    "Buy EURUSD @ 1.12345, SL: 1.12000, TP1: 1.13000, TP2: 1.13500, TP3: 1.14000",
    "Sell BTCUSD @ 30000, TP1: 31000, TP2: 32000",
    "Buy GBPUSD @ 1.25000, TP1: 1.25500",
    "Invalid message without proper format"
]

# Testlauf
for message in test_messages:
    signal = parse_signal(message)
    if signal:
        print(f"Signal erkannt: {signal}")
    else:
        print(f"Ungültige Nachricht: {message}")
