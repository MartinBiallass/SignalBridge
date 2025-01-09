from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime
from config import SIGNALGEBER_DB, PERFORMANCE_DB

app = Flask(__name__)

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

# Performance-Daten laden
def load_performance():
    try:
        with open(PERFORMANCE_DB, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "platform": "",
            "broker": "",
            "account_type": "",
            "initial_balance": 0.0,
            "current_balance": 0.0,
            "total_profit": 0.0,
            "monthly_profit": 0.0,
            "weekly_profit": 0.0,
            "daily_profit": 0.0,
            "last_update": ""
        }

# Performance-Daten speichern
def save_performance(data):
    with open(PERFORMANCE_DB, "w") as file:
        json.dump(data, file, indent=4)

@app.route("/")
def dashboard():
    signalgeber = load_signalgeber()
    performance = load_performance()  # Lädt Performance-Daten
    return render_template("dashboard.html", signalgeber=signalgeber, performance=performance)

@app.route("/adjust_sl_tp/<channel_id>", methods=["POST"])
def adjust_sl_tp(channel_id):
    signalgeber = load_signalgeber()
    if channel_id not in signalgeber:
        return jsonify({"success": False, "message": "Signalgeber nicht gefunden"}), 404

    try:
        sl = request.form.get("sl")
        tp = request.form.get("tp")
        if sl:
            signalgeber[channel_id].setdefault("settings", {})["sl"] = float(sl)
        if tp:
            signalgeber[channel_id].setdefault("settings", {})["tp"] = float(tp)
        signalgeber[channel_id]["timestamp"] = datetime.utcnow().isoformat()
        save_signalgeber(signalgeber)
        return jsonify({"success": True, "message": "SL/TP erfolgreich aktualisiert", "sl": sl, "tp": tp})
    except ValueError:
        return jsonify({"success": False, "message": "Ungültige Eingabe"}), 400

@app.route("/toggle/<channel_id>", methods=["POST"])
def toggle_signalgeber(channel_id):
    signalgeber = load_signalgeber()
    if channel_id in signalgeber:
        signalgeber[channel_id]["active"] = not signalgeber[channel_id].get("active", False)
        signalgeber[channel_id]["timestamp"] = datetime.utcnow().isoformat()
        save_signalgeber(signalgeber)
        status = "aktiviert" if signalgeber[channel_id]["active"] else "deaktiviert"
        return jsonify({"success": True, "message": f"Signalgeber wurde {status}."})
    return jsonify({"success": False, "message": "Signalgeber nicht gefunden"}), 404

@app.route("/filter", methods=["GET"])
def filter_signalgeber():
    status = request.args.get("status", "").lower()
    signalgeber = load_signalgeber()
    if status in ["aktiv", "inaktiv"]:
        filtered = {
            k: v for k, v in signalgeber.items()
            if ("aktiv" if v.get("active", False) else "inaktiv") == status
        }
        return render_template("dashboard.html", signalgeber=filtered)
    return render_template("dashboard.html", signalgeber=signalgeber)

if __name__ == "__main__":
    app.run(debug=True)
@app.route("/update_signalgeber/<channel_id>", methods=["POST"])
def update_signalgeber(channel_id):
    data = request.json
    signalgeber = load_signalgeber()
    
    if channel_id in signalgeber:
        signalgeber[channel_id]["settings"]["risk_management"] = data.get("risk_management", {})
        signalgeber[channel_id]["settings"]["tp_sl_strategy"] = data.get("tp_sl_strategy", {})
        signalgeber[channel_id]["settings"]["filters"] = data.get("filters", {})
        save_signalgeber(signalgeber)
        return jsonify({"success": True, "message": "Einstellungen aktualisiert"})
    return jsonify({"success": False, "message": "Signalgeber nicht gefunden"}), 404
