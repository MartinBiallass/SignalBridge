from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Sprachkonfigurationen
translations = {
    "de": {
        "home": "Startseite",
        "linked_accounts": "Verknüpfte Konten",
        "account_management": "Kontoverwaltung",
        "message_history": "Nachrichtenverlauf",
        "health_check": "System Cockpit",
        "backtest": "Backtest",
        "support": "Support",
        "help": "Hilfe",
        "welcome": "Willkommen bei SignalBridge",
        "select_area": "Wählen Sie einen Bereich aus der Navigation, um loszulegen."
    },
    "en": {
        "home": "Home Page",
        "linked_accounts": "Linked Accounts",
        "account_management": "Account Management",
        "message_history": "Message History",
        "health_check": "System Cockpit",
        "backtest": "Backtest",
        "support": "Support",
        "help": "Help",
        "welcome": "Welcome to SignalBridge",
        "select_area": "Select a section from the navigation to get started."
    }
}

@app.route("/")
def home():
    lang = session.get("language", "de")
    return render_template("dashboard.html", section="home", lang=lang, translations=translations[lang])

@app.route("/linked-accounts")
def linked_accounts():
    lang = session.get("language", "de")
    accounts = [
        {"name": "Beispielkonto 1", "platform": "Telegram", "status": "Aktiv"},
        {"name": "Beispielkonto 2", "platform": "Discord", "status": "Inaktiv"}
    ]
    return render_template(
        "dashboard.html",
        section="linked_accounts",
        lang=lang,
        translations=translations[lang],
        accounts=accounts
    )

@app.route("/account-management")
def account_management():
    lang = session.get("language", "de")
    return render_template("dashboard.html", section="account_management", lang=lang, translations=translations[lang])

@app.route("/message-history", methods=["GET"])
def message_history():
    lang = session.get("language", "de")
    with open("data/messages.json", "r") as file:
        messages = json.load(file)

    channels = list(set(msg["channel"] for msg in messages))
    selected_channel = request.args.get("channel", "all")

    if selected_channel != "all":
        messages = [msg for msg in messages if msg["channel"] == selected_channel]

    return render_template(
        "dashboard.html",
        section="message_history",
        lang=lang,
        translations=translations[lang],
        messages=messages,
        channels=channels,
        selected_channel=selected_channel
    )

@app.route("/system-cockpit")
def system_cockpit():
    lang = session.get("language", "de")
    system_status = {
        "telegram_status": "Verbunden",
        "server_status": "Läuft",
        "local_server_status": "Aktiv",
        "api_status": "Verbunden",
        "software_version": "1.0.3",
        "analyzer_version": "1.1.0",
        "functions_version": "2.0.5",
        "interface_version": "1.0.0"
    }
    current_ram = 3.16
    total_ram = 4.0
    ram_percentage = (current_ram / total_ram) * 100
    ram_status = "ok" if ram_percentage <= 70 else "warn" if ram_percentage <= 90 else "critical"

    return render_template(
        "dashboard.html",
        section="health_check",
        lang=lang,
        translations=translations[lang],
        system_status=system_status,
        current_ram=f"{current_ram:.2f} GB",
        total_ram=f"{total_ram:.2f} GB",
        ram_status=ram_status
    )


@app.route("/backtest")
def backtest():
    lang = session.get("language", "de")
    return render_template(
        "dashboard.html",
        section="backtest",
        lang=lang,
        translations=translations[lang]
    )


@app.route("/support")
def support():
    lang = session.get("language", "de")
    return render_template("dashboard.html", section="support", lang=lang, translations=translations[lang])

@app.route("/help")
def help():
    lang = session.get("language", "de")
    return render_template("dashboard.html", section="help", lang=lang, translations=translations[lang])

@app.route("/set_language", methods=["POST"])
def set_language():
    session["language"] = request.form.get("language", "de")
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)
