from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime
import re

app = Flask(__name__)

# Datei für die Signalgeber-Datenbank
SIGNALGEBER_DB = "signalgeber.json"

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

# Parsing-Funktion für Signale
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
            "timestamp": datetime.utcnow().isoformat()
        }
    return None

@app.route("/")
def dashboard():
    signalgeber = load_signalgeber()
    return render_template("dashboard.html", signalgeber=signalgeber)

@app.route("/toggle/<channel_id>", methods=["POST"])
def toggle_signalgeber(channel_id):
    signalgeber = load_signalgeber()
    if channel_id in signalgeber:
        signalgeber[channel_id]["active"] = not signalgeber[channel_id]["active"]
        signalgeber[channel_id]["timestamp"] = datetime.utcnow().isoformat()
        save_signalgeber(signalgeber)
        return jsonify({"success": True, "status": signalgeber[channel_id]["active"]})
    return jsonify({"success": False, "message": "Signalgeber nicht gefunden"}), 404

# Neue Route für Signalverarbeitung
@app.route("/process_signal", methods=["POST"])
def process_signal():
    data = request.get_json()
    message = data.get("message", "")
    signal = parse_signal(message)
    if signal:
        return jsonify({"success": True, "signal": signal})
    return jsonify({"success": False, "message": "Ungültiges Signalformat"}), 400

if __name__ == "__main__":
    app.run(debug=True)
