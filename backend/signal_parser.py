import re
from datetime import datetime
import json

# JSON-Datei mit den bekannten Symbolen laden
def load_symbols(json_path):
    with open(json_path, "r") as file:
        data = json.load(file)
    known_symbols = set()
    for category, instruments in data["categories"].items():
        for instrument in instruments:
            known_symbols.add(instrument["symbol"])
    return known_symbols

# JSON-Dateipfad
json_path = "data/trading_instruments.json"
known_symbols = load_symbols(json_path)

def parse_signal_with_validation(message):
    """
    Signal-Parser mit Symbolvalidierung gegen eine bekannte Liste.
    """
    # Bereinigen der Nachricht von Emojis und nicht-relevanten Zeichen
    clean_message = re.sub(r"[^\w\s@.:,-/]", "", message)

    # Hauptmuster: Aktion, Symbol und Entry-Preis
    main_pattern = r"(?i)(Buy|Sell|Long|Short)\s+([\w/]+)\s*@?\s*([\d.]+)"
    main_match = re.search(main_pattern, clean_message)

    if not main_match:
        return None  # Kein gültiges Hauptsignal gefunden

    # Initialisiere das Signal
    symbol = main_match.group(2).upper()
    if symbol not in known_symbols:
        return None  # Symbol ist nicht bekannt und wird ignoriert

    signal = {
        "action": main_match.group(1).capitalize(),
        "symbol": symbol,
        "entry_price": float(main_match.group(3)),
        "stop_loss": None,
        "take_profits": [],
        "timestamp": datetime.now().isoformat()
    }

    # Stop Loss extrahieren
    sl_pattern = r"(?i)(SL|Stop Loss)[:\s-]*([\d.]+)"
    sl_match = re.search(sl_pattern, clean_message)
    if sl_match:
        signal["stop_loss"] = float(sl_match.group(2))

    # Alle Take-Profit-Level extrahieren (inklusive Varianten wie "Target")
    tp_pattern = r"(?i)(TP|Target)\d?[:\s-]*([\d.]+)"
    for tp_match in re.finditer(tp_pattern, clean_message):
        signal["take_profits"].append(float(tp_match.group(2)))

    return signal

# Testnachrichten mit validierter Symbolerkennung
final_test_messages = [
    "👉 GBPJPY@195.47~ SELL\n\n💰 SL - 196.07\n\n💰 TP1 - 195.27\n💰 TP2 - 194.87\n💰 TP3 - 193.87",
    "SELL - GBPCHF @ 1.12270\n• SL @ 1.12930\nTP1 @ 1.12070\nTP2 @ 1.11670\nTP3 @ 1.10670",
    "✨EURJPY weekly analysis✨\nsell EURJPY 163.80\nSL 165.30\nTP1 161.80\nTP2 159.80",
    "EURAUD sell now @ 1.6630\nSL @ 1.6670 (40 pips)\nTP @ 1.6570\nTP2 @ 1.6470",
    "LQTY/USDT LONG 🌟\nLeverage 10x\nEntries 2.038\nTarget 1 2.1\nTarget 2 2.16\nTarget 3 2.24\nSL 1.915",
    "XAUUSD daily analysis\nsell XAUUSD 2670.00\nSL 2685.00\nTP1 2650.00\nTP2 2630.00"
]

# Testlauf
if __name__ == "__main__":
    for message in final_test_messages:
        result = parse_signal_with_validation(message)
        print("Input:", message)
        print("Parsed Signal:", result)
        print("-" * 50)
