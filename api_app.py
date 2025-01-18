from flask import Blueprint, request, jsonify
import json
import os

api_app = Blueprint("api_app", __name__)

# Dateipfad für die Risikoeinstellungen
RISK_MANAGEMENT_FILE = "data/risk_management.json"
KEYWORDS_FILE = "data/signal_keywords.json"

# Utility-Funktionen

def load_risk_management():
    """Lade die Risikoeinstellungen."""
    if not os.path.exists(RISK_MANAGEMENT_FILE):
        return {"signal_providers": {}}
    with open(RISK_MANAGEMENT_FILE, "r") as file:
        return json.load(file)

def save_risk_management(data):
    """Speichere die Risikoeinstellungen."""
    with open(RISK_MANAGEMENT_FILE, "w") as file:
        json.dump(data, file, indent=4)

def load_keywords():
    """Lade die Schlüsselwörter für Signalgeber."""
    if not os.path.exists(KEYWORDS_FILE):
        return {}
    with open(KEYWORDS_FILE, "r") as file:
        return json.load(file)

def save_keywords(data):
    """Speichere die Schlüsselwörter für Signalgeber."""
    with open(KEYWORDS_FILE, "w") as file:
        json.dump(data, file, indent=4)

# API-Endpunkte

@api_app.route("/get_risk_settings/<provider>", methods=["GET"])
def get_risk_settings(provider):
    """Hole die Risikoeinstellungen eines Signalgebers."""
    data = load_risk_management()
    settings = data.get("signal_providers", {}).get(provider, {})
    return jsonify(settings)

@api_app.route("/update_risk_settings/<provider>", methods=["POST"])
def update_risk_settings(provider):
    """Aktualisiere die Risikoeinstellungen eines Signalgebers."""
    try:
        new_settings = request.get_json()
        data = load_risk_management()
        if "signal_providers" not in data:
            data["signal_providers"] = {}
        data["signal_providers"][provider] = new_settings
        save_risk_management(data)
        return jsonify({"message": "Risk settings updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_app.route("/calculate_lot_size", methods=["POST"])
def calculate_lot_size():
    """Berechne die Lotgröße basierend auf den Risikoeinstellungen."""
    try:
        request_data = request.get_json()
        provider = request_data.get("provider", "default_provider")
        account_balance = request_data.get("account_balance", 0)
        stop_loss_pips = request_data.get("stop_loss_pips", 0)
        pip_value = request_data.get("pip_value", 0)

        # Lade die Risikoeinstellungen
        data = load_risk_management()
        provider_settings = data.get("signal_providers", {}).get(provider, {})

        risk_mode = provider_settings.get("risk_mode", "percent")
        risk_value = provider_settings.get("risk_value", 0)
        fixed_amount = provider_settings.get("fixed_amount", 0)

        # Berechne das Risiko
        if risk_mode == "percent":
            risk_amount = (risk_value / 100) * account_balance
        elif risk_mode == "fixed":
            risk_amount = fixed_amount
        else:
            return jsonify({"error": "Invalid risk mode"}), 400

        # Berechnung der Lotgröße
        lot_size = round(risk_amount / (stop_loss_pips * pip_value), 2)
        return jsonify({
            "provider": provider,
            "account_balance": account_balance,
            "risk_mode": risk_mode,
            "risk_value": risk_value,
            "fixed_amount": fixed_amount,
            "calculated_lot_size": lot_size
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_app.route("/get_keywords/<provider>", methods=["GET"])
def get_keywords(provider):
    """Hole die Schlüsselwörter eines Signalgebers."""
    data = load_keywords()
    keywords = data.get(provider, {})
    return jsonify(keywords)

@api_app.route("/update_keywords/<provider>", methods=["POST"])
def update_keywords(provider):
    """Aktualisiere die Schlüsselwörter eines Signalgebers."""
    try:
        new_keywords = request.get_json()
        data = load_keywords()
        data[provider] = new_keywords
        save_keywords(data)
        return jsonify({"message": "Keywords updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_app.route("/process_message", methods=["POST"])
def process_message():
    """Verarbeite eine Nachricht basierend auf den Schlüsselwörtern."""
    try:
        data = request.get_json()
        signal_provider = data.get("signal_provider", "default")
        message = data.get("message", "").lower()

        # Lade Schlüsselwörter für den Signalgeber
        keywords = load_keywords().get(signal_provider, {})

        # Prüfe Nachricht auf Schlüsselwörter
        actions = []

        if any(keyword in message for keyword in keywords.get("close_signal", [])):
            actions.append("close_signal")
        if any(keyword in message for keyword in keywords.get("close_half", [])):
            actions.append("close_half")
        if any(keyword in message for keyword in keywords.get("move_sl_entry", [])):
            actions.append("move_sl_entry")
        if any(keyword in message for keyword in keywords.get("remove_sl", [])):
            actions.append("remove_sl")
        if any(keyword in message for keyword in keywords.get("close_pending_order", [])):
            actions.append("close_pending_order")

        # Rückgabe der erkannten Aktionen
        return jsonify({"recognized_actions": actions})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
