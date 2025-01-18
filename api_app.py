from flask import Blueprint, request, jsonify
import json
import os

api_app = Blueprint("api_app", __name__)

# Dateipfade für Daten
KEYWORDS_FILE = "data/signal_keywords.json"
TRADES_FILE = "data/trades.json"

# Hilfsfunktionen
def load_keywords():
    """Lade die Schlüsselwörter aus der Datei."""
    if not os.path.exists(KEYWORDS_FILE):
        return {}
    with open(KEYWORDS_FILE, "r") as file:
        return json.load(file)

def save_keywords(data):
    """Speichere die Schlüsselwörter in die Datei."""
    with open(KEYWORDS_FILE, "w") as file:
        json.dump(data, file, indent=4)

def load_trades():
    """Lade die aktuellen Trades."""
    if not os.path.exists(TRADES_FILE):
        return {}
    with open(TRADES_FILE, "r") as file:
        return json.load(file)

def save_trades(data):
    """Speichere die aktuellen Trades."""
    with open(TRADES_FILE, "w") as file:
        json.dump(data, file, indent=4)

# API-Routen

@api_app.route("/get_keywords/<provider>", methods=["GET"])
def get_keywords(provider):
    """Hole die Schlüsselwörter für einen Signalgeber."""
    keywords = load_keywords()
    return jsonify(keywords.get(provider, {}))

@api_app.route("/update_keywords/<provider>", methods=["POST"])
def update_keywords(provider):
    """Aktualisiere die Schlüsselwörter für einen Signalgeber."""
    try:
        new_keywords = request.get_json()
        keywords = load_keywords()
        keywords[provider] = new_keywords
        save_keywords(keywords)
        return jsonify({"message": "Keywords updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_app.route("/process_signal", methods=["POST"])
def process_signal():
    """Verarbeite ein Signal basierend auf den Schlüsselwörtern."""
    try:
        signal_data = request.get_json()
        provider = signal_data.get("provider", "default_provider")
        message = signal_data.get("message", "")

        # Lade die Schlüsselwörter
        keywords = load_keywords()
        provider_keywords = keywords.get(provider, {})

        # Lade Trades
        trades = load_trades()

        # Aktionen basierend auf Schlüsselwörtern
        actions = []

        if "change_sl" in provider_keywords and provider_keywords["change_sl"] in message:
            new_sl = extract_number_from_message(message, provider_keywords["change_sl"])
            trades["stop_loss"] = new_sl
            actions.append(f"Stop Loss updated to {new_sl}")

        if "change_tp" in provider_keywords and provider_keywords["change_tp"] in message:
            new_tp = extract_number_from_message(message, provider_keywords["change_tp"])
            trades["take_profit"] = new_tp
            actions.append(f"Take Profit updated to {new_tp}")

        if "change_entry" in provider_keywords and provider_keywords["change_entry"] in message:
            new_entry = extract_number_from_message(message, provider_keywords["change_entry"])
            trades["entry_point"] = new_entry
            actions.append(f"Entry Point updated to {new_entry}")

        if "reenter" in provider_keywords and provider_keywords["reenter"] in message:
            actions.append("Re-enter trade executed")

        if "close_half" in provider_keywords and provider_keywords["close_half"] in message:
            actions.append("Half of the position closed")

        if "move_sl_to_entry" in provider_keywords and provider_keywords["move_sl_to_entry"] in message:
            trades["stop_loss"] = trades.get("entry_point", trades.get("stop_loss"))
            actions.append("Stop Loss moved to entry point")

        # Speichere die aktualisierten Trades
        save_trades(trades)

        return jsonify({"actions": actions, "updated_trades": trades})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Hilfsfunktion für die Extraktion von Zahlen
def extract_number_from_message(message, keyword):
    """Extrahiere eine Zahl aus einer Nachricht nach einem Schlüsselwort."""
    try:
        keyword_index = message.lower().find(keyword.lower())
        if keyword_index == -1:
            return None
        after_keyword = message[keyword_index + len(keyword):]
        number = "".join(c for c in after_keyword if c.isdigit() or c == ".").strip()
        return float(number) if number else None
    except Exception as e:
        return None

@api_app.route("/close_trade", methods=["POST"])
def close_trade():
    """Schließe einen Trade vollständig."""
    try:
        trade_data = request.get_json()
        trade_id = trade_data.get("trade_id")

        # Lade Trades
        trades = load_trades()

        if trade_id in trades:
            del trades[trade_id]
            save_trades(trades)
            return jsonify({"message": f"Trade {trade_id} closed successfully"})
        else:
            return jsonify({"error": "Trade not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400
