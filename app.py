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
        "select_area": "Wählen Sie einen Bereich aus der Navigation, um loszulegen.",
        "performance_overview": "Performance Übersicht",
        "select_account": "Wählen Sie ein Konto aus:",
        "account_protection": "Konto Schutz"
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
        "select_area": "Select a section from the navigation to get started.",
        "performance_overview": "Performance Overview",
        "select_account": "Select an account:",
        "account_protection": "Equity Guardian"
    }
}

@app.route("/")
def home():
    lang = session.get("language", "de")
    return render_template("dashboard.html", section="home", lang=lang, translations=translations[lang])

@app.route("/linked-accounts")
def linked_accounts():
    lang = session.get("language", "de")
    try:
        with open("data/accounts.json", "r") as file:
            accounts = json.load(file)
    except FileNotFoundError:
        accounts = []
    return render_template(
        "dashboard.html",
        section="linked_accounts",
        lang=lang,
        translations=translations[lang],
        accounts=accounts
    )

@app.route("/account-management", methods=["GET", "POST"])
def account_management():
    lang = session.get("language", "de")
    with open("data/accounts.json", "r") as file:
        accounts = json.load(file)

    if request.method == "POST":
        selected_account = request.form.get("account")
        account = next((acc for acc in accounts if acc["account_name"] == selected_account), None)
        return render_template(
            "dashboard.html",
            section="performance_overview",
            lang=lang,
            translations=translations[lang],
            account=account
        )

    return render_template(
        "dashboard.html",
        section="account_management",
        lang=lang,
        translations=translations[lang],
        accounts=accounts
    )

@app.route("/performance-overview")
def performance_overview():
    lang = session.get("language", "de")
    # Testdaten für Performance
    performance_data = {
        "profit_total": 1200.50,
        "profit_month": 300.25,
        "profit_week": 75.60,
        "initial_balance": 5000.00,
        "drawdown": 2.34
    }
    return render_template(
        "dashboard.html",
        section="performance_overview",
        lang=lang,
        translations=translations[lang],
        performance=performance_data
    )

@app.route("/provider-details/<provider_name>")
def provider_details(provider_name):
    lang = session.get("language", "de")
    with open("data/accounts.json", "r") as file:
        accounts = json.load(file)
    
    provider_data = None
    for account in accounts:
        for provider in account.get("performance", []):
            if provider["name"] == provider_name:
                provider_data = provider
                break
    
    if not provider_data:
        return "Provider not found", 404

    return render_template(
        "dashboard.html",
        section="provider_details",
        lang=lang,
        translations=translations[lang],
        provider=provider_data
    )

@app.route("/message-history", methods=["GET"])
def message_history():
    lang = session.get("language", "de")
    try:
        with open("data/messages.json", "r") as file:
            messages = json.load(file)
    except FileNotFoundError:
        messages = []

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
        # Hier können wir die Support-Anfrage speichern oder weiterleiten
        print(f"Betreff: {subject}, Beschreibung: {description}, Datei: {file.filename if file else 'Keine Datei'}")
        return jsonify({"success": True, "message": "Support-Anfrage erfolgreich gesendet"})
    return render_template("dashboard.html", section="support", lang=lang, translations=translations[lang])

@app.route("/help")
def help():
    lang = session.get("language", "de")
    faqs = [
        {"question": "Wie verbinde ich Telegram?", "answer": "Gehen Sie zu den Einstellungen und klicken Sie auf 'Telegram verbinden'."},
        {"question": "Wie passe ich mein Konto an?", "answer": "Gehen Sie zu 'Kontoverwaltung' und bearbeiten Sie die Einstellungen."},
        {"question": "Was mache ich bei Verbindungsproblemen?", "answer": "Überprüfen Sie Ihre Internetverbindung und versuchen Sie es erneut."}
    ]
    return render_template("dashboard.html", section="help", lang=lang, translations=translations[lang], faqs=faqs)

@app.route("/set_language", methods=["POST"])
def set_language():
    session["language"] = request.form.get("language", "de")
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)
