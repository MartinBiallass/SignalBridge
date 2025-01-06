import re
from flask import Flask, request, jsonify, render_template
import json
from datetime import datetime

# Flask-App definieren
app = Flask(__name__)

# Datei für die Signalgeber-Datenbank
SIGNALGEBER_DB = "signalgeber.json"
PROCESSED_SIGNALS_FILE = "processed_signals.json"

# Signalgeber-Daten laden
def load_signalgeber():
    try:
        with open(SIGNALGEBER_DB, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Signalgeber-Daten speichern
def save_signalgeber(data):
    with open(SIGNALGEBER_DB, "w") as file:
        json.dump(data, file, indent=4)

# Datei für Signale laden
def load_signals():
    try:
        with open(PROCESSED_SIGNALS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"signals": []}

# Datei für Signale speichern
def save_signal(signal):
    data = load_signals()
    data["signals"].append(signal)
    with open(PROCESSED_SIGNALS_FILE, "w") as file:
        json.dump(data, file, indent=4)
    print(f"Signal gespeichert: {signal}")

# Signal-Parsing-Funktion
def parse_signal(message, use_market_price=False):
    try:
        signal_pattern = r"(Buy|Sell)\s+(\w+)\s+@\s+([\d.]+)(?:,\s*SL:\s*([\d.]+))?(?:,\s*TP1:\s*([\d.]+))?(?:,\s*TP2:\s*([\d.]+))?(?:,\s*TP3:\s*([\d.]+))?"
        match = re.search(signal_pattern, message, re.IGNORECASE)

        if match:
            return {
                "action": match.group(1),
                "symbol": match.group(2),
                "entry_price": float(match.group(3)) if not use_market_price else None,
                "stop_loss": float(match.group(4)) if match.group(4) else None,
                "tp_values": {
                    "TP1": float(match.group(5)) if match.group(5) else None,
                    "TP2": float(match.group(6)) if match.group(6) else None,
                    "TP3": float(match.group(7)) if match.group(7) else None,
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        return None
    except Exception as e:
        print(f"Fehler beim Parsing: {e}")
        return None

# Dashboard-Route
@app.route("/")
def dashboard():
    signalgeber = load_signalgeber()
    return render_template("dashboard.html", signalgeber=signalgeber)

# Route zum Umschalten der Signalgeber
@app.route("/toggle/<channel_id>", methods=["POST"])
def toggle_signalgeber(channel_id):
    signalgeber = load_signalgeber()
    if channel_id in signalgeber:
        signalgeber[channel_id]["active"] = not signalgeber[channel_id]["active"]
        signalgeber[channel_id]["timestamp"] = datetime.utcnow().isoformat()
        save_signalgeber(signalgeber)
        return jsonify({"success": True, "status": signalgeber[channel_id]["active"]})
    return jsonify({"success": False, "message": "Signalgeber nicht gefunden"}), 404

# Route zur Verarbeitung von Signalen
@app.route("/process_signal", methods=["POST"])
def process_signal():
    data = request.json
    message = data.get("message")
    use_market_price = data.get("use_market_price", False)

    # Signal-Parsing
    signal = parse_signal(message, use_market_price)

    if signal:
        save_signal(signal)
        return jsonify({"success": True, "signal": signal})
    else:
        return jsonify({"success": False, "error": "Kein gültiges Signal erkannt"}), 400

if __name__ == "__main__":
    app.run(debug=True)
def parse_signal(message, use_market_price=False):
    print(f"Parsing Nachricht: {message}")  # Debug-Ausgabe
    try:
        signal_pattern = r"(Buy|Sell)\s+(\w+)\s+@\s+([\d.]+)(?:,\s*SL:\s*([\d.]+))?(?:,\s*TP1:\s*([\d.]+))?(?:,\s*TP2:\s*([\d.]+))?(?:,\s*TP3:\s*([\d.]+))?"
        match = re.search(signal_pattern, message, re.IGNORECASE)

        if match:
            signal = {
                "action": match.group(1),
                "symbol": match.group(2),
                "entry_price": float(match.group(3)) if not use_market_price else None,
                "stop_loss": float(match.group(4)) if match.group(4) else None,
                "tp_values": {
                    "TP1": float(match.group(5)) if match.group(5) else None,
                    "TP2": float(match.group(6)) if match.group(6) else None,
                    "TP3": float(match.group(7)) if match.group(7) else None,
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            print(f"Erkanntes Signal: {signal}")  # Debug-Ausgabe
            return signal
        else:
            print("Kein Treffer mit dem Parsing-Muster.")  # Debug-Ausgabe
            return None
    except Exception as e:
        print(f"Fehler beim Parsing: {e}")
        return None
