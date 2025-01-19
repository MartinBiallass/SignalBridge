from flask import Blueprint, request, jsonify
import json
import os

api_app = Blueprint("api_app", __name__)

# Dateipfade für Daten
KEYWORDS_FILE = "data/signal_keywords.json"
TRADES_FILE = "data/trades.json"
SETTINGS_FILE = "data/settings.json"  # Neue Datei für benutzerdefinierte Einstellungen

# Hilfsfunktionen
def load_settings():
    """Lade die benutzerdefinierten Einstellungen."""
    if not os.path.exists(SETTINGS_FILE):
        return {}
    with open(SETTINGS_FILE, "r") as file:
        return json.load(file)

def save_settings(data):
    """Speichere die benutzerdefinierten Einstellungen."""
    with open(SETTINGS_FILE, "w") as file:
        json.dump(data, file, indent=4)

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

@api_app.route("/update_settings", methods=["POST"])
def update_settings():
    """Aktualisiere die Einstellungen."""
    try:
        new_settings = request.get_json()
        settings = load_settings()
        settings.update(new_settings)
        save_settings(settings)
        return jsonify({"message": "Settings updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_app.route("/get_settings", methods=["GET"])
def get_settings():
    """Hole die aktuellen Einstellungen."""
    try:
        settings = load_settings()
        return jsonify(settings)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_app.route("/process_signal", methods=["POST"])
def process_signal():
    """Verarbeite ein Signal basierend auf den Schlüsselwörtern und den Einstellungen."""
    try:
        signal_data = request.get_json()
        provider = signal_data.get("provider", "default_provider")
        message = signal_data.get("message", "")
        settings = load_settings()

        # Lade Trades und Keywords
        trades = load_trades()
        keywords = load_keywords()
        provider_keywords = keywords.get(provider, {})

        actions = []

        # Neue Funktion: Limitierung offener Trades
        max_trades = settings.get("max_open_trades", None)
        if max_trades and len(trades) >= max_trades:
            actions.append("Trade limit reached. Signal ignored.")
            return jsonify({"actions": actions, "updated_trades": trades})

        # Randomize Magic Numbers (Dummy-Implementierung)
        if settings.get("randomize_magic_number", False):
            magic_number = os.urandom(4).hex()
            actions.append(f"Magic number randomized: {magic_number}")

        # Beispiel: Verarbeitung neuer Trades
        if "new_trade" in provider_keywords:
            for keyword in provider_keywords["new_trade"]:
                if keyword.lower() in message.lower():
                    trade_details = parse_new_trade(message)
                    if trade_details:
                        if not is_duplicate_trade(trade_details, trades):
                            trade_id = f"trade_{len(trades) + 1}"
                            trades[trade_id] = trade_details
                            actions.append(f"New trade added: {trade_details}")
                        else:
                            actions.append(f"Duplicate trade ignored: {trade_details}")

        # Bedingungen zum Schließen von Trades
        if "close_conditions" in provider_keywords:
            for condition in provider_keywords["close_conditions"]:
                if condition in message:
                    trades_to_close = apply_close_conditions(trades, condition)
                    for trade_id in trades_to_close:
                        del trades[trade_id]
                        actions.append(f"Trade {trade_id} closed due to condition: {condition}")

        # Speichere die aktualisierten Trades
        save_trades(trades)
        return jsonify({"actions": actions, "updated_trades": trades})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Neue Hilfsfunktion zur Verarbeitung von Schließbedingungen
def apply_close_conditions(trades, condition):
    """Wende Schließbedingungen auf die Trades an."""
    trades_to_close = []
    for trade_id, trade in trades.items():
        # Beispiel: Schließe Trades basierend auf einer Bedingung
        if condition == "example_condition":
            trades_to_close.append(trade_id)
    return trades_to_close

# Optimierte Hilfsfunktion zur Überprüfung auf Duplikate
def is_duplicate_trade(new_trade, trades):
    """Prüfe, ob ein neuer Trade ein Duplikat eines bestehenden ist."""
    try:
        existing_trades_set = {
            (trade.get("entry_point"), trade.get("stop_loss"), trade.get("take_profit"), trade.get("symbol"))
            for trade in trades.values() if isinstance(trade, dict)
        }
        new_trade_tuple = (
            new_trade.get("entry_point"),
            new_trade.get("stop_loss"),
            new_trade.get("take_profit"),
            new_trade.get("symbol"),
        )
        return new_trade_tuple in existing_trades_set
    except Exception as e:
        return False

# Hilfsfunktion für die Verarbeitung neuer Trades
def parse_new_trade(message):
    """Parsiere eine Nachricht, um Details für einen neuen Trade zu extrahieren."""
    try:
        parts = message.split(",")
        trade = {}
        for part in parts:
            if "entry" in part.lower():
                trade["entry_point"] = float(part.split()[-1])
            elif "sl" in part.lower():
                trade["stop_loss"] = float(part.split()[-1])
            elif "tp" in part.lower():
                trade["take_profit"] = float(part.split()[-1])
            elif "buy" in part.lower() or "sell" in part.lower():
                trade["type"] = part.split()[0].capitalize()
                trade["symbol"] = part.split()[1].upper()
        return trade if "entry_point" in trade and "stop_loss" in trade and "take_profit" in trade else None
    except Exception as e:
        return None
