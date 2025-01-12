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
    dummy_messages = [
        {"timestamp": "2025-01-10 12:00", "channel": "CryptoAlerts", "message": "BTC/USD Buy @ 35000"},
        {"timestamp": "2025-01-10 12:05", "channel": "ForexSignals", "message": "EUR/USD Sell @ 1.1000"},
        {"timestamp": "2025-01-10 12:10", "channel": "StockMarket", "message": "AAPL Buy @ 150"},
    ]
    channels = list(set(msg["channel"] for msg in dummy_messages))
    selected_channel = request.args.get("channel", "all")
    filtered_messages = dummy_messages if selected_channel == "all" else [msg for msg in dummy_messages if msg["channel"] == selected_channel]

    return render_template(
        "dashboard.html",
        section="message_history",
        lang=lang,
        translations=translations[lang],
        messages=filtered_messages,
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
        section="system_cockpit",
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

@app.route("/support", methods=["GET", "POST"])
def support():
    lang = session.get("language", "de")
    if request.method == "POST":
        subject = request.form.get("subject")
        description = request.form.get("description")
        file = request.files.get("attachment")
        # Hier könnten wir die Datei speichern oder weitere Verarbeitung vornehmen.
        print(f"Betreff: {subject}, Beschreibung: {description}, Datei: {file.filename if file else 'Keine Datei'}")
    return render_template("dashboard.html", section="support", lang=lang, translations=translations[lang])

@app.route("/help")
def help():
    lang = session.get("language", "de")
    faqs = [
        {"id": "faq1", "title": "Wie verbinde ich Telegram?", "content": "Gehen Sie zu den Einstellungen und klicken Sie auf 'Telegram verbinden'."},
        {"id": "faq2", "title": "Wie passe ich mein Konto an?", "content": "Gehen Sie zu 'Kontoverwaltung' und bearbeiten Sie die Einstellungen."},
        {"id": "faq3", "title": "Was mache ich bei Verbindungsproblemen?", "content": "Überprüfen Sie Ihre Internetverbindung und versuchen Sie es erneut."}
    ]
    return render_template(
        "dashboard.html",
        section="help",
        lang=lang,
        translations=translations[lang],
        faqs=faqs
    )

@app.route("/set_language", methods=["POST"])
def set_language():
    session["language"] = request.form.get("language", "de")
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)
