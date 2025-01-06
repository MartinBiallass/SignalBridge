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

@app.route("/toggle/<channel_id>", methods=["POST"])
def toggle_signalgeber(channel_id):
    signalgeber = load_signalgeber()
    if channel_id in signalgeber:
        signalgeber[channel_id]["active"] = not signalgeber[channel_id]["active"]
        signalgeber[channel_id]["timestamp"] = datetime.utcnow().isoformat()
        save_signalgeber(signalgeber)
        return jsonify({"success": True, "status": signalgeber[channel_id]["active"]})
    return jsonify({"success": False, "message": "Signalgeber nicht gefunden"}), 404

if __name__ == "__main__":
    app.run(debug=True)

