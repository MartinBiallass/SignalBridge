from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime

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

@app.route("/")
def dashboard():
    signalgeber = load_signalgeber()
    return render_template("dashboard.html", signalgeber=signalgeber)

@app.route("/adjust_sl_tp/<channel_id>", methods=["POST"])
def adjust_sl_tp(channel_id):
    data = load_signalgeber()
    if channel_id not in data:
        return jsonify({"success": False, "message": "Signalgeber nicht gefunden"}), 404

    try:
        sl = float(request.form.get("sl"))
        tp = float(request.form.get("tp"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Ungültige Eingabewerte"}), 400

    # Werte aktualisieren
    data[channel_id]["settings"]["sl"] = sl
    data[channel_id]["settings"]["tp"] = tp
    save_signalgeber(data)
    return jsonify({"success": True, "message": f"SL und TP für {data[channel_id]['name']} aktualisiert!"})

@app.route("/toggle/<channel_id>", methods=["POST"])
def toggle_signalgeber(channel_id):
    data = load_signalgeber()
    if channel_id in data:
        data[channel_id]["active"] = not data[channel_id]["active"]
        data[channel_id]["timestamp"] = datetime.utcnow().isoformat()
        save_signalgeber(data)
        return jsonify({"success": True, "status": data[channel_id]["active"]})
    return jsonify({"success": False, "message": "Signalgeber nicht gefunden"}), 404

if __name__ == "__main__":
    app.run(debug=True)
