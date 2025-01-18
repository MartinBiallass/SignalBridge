from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import json
from api_app import api_app  # Importiere den Blueprint

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Registrierung der API
app.register_blueprint(api_app, url_prefix="/api")

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

if __name__ == "__main__":
    app.run(debug=True)
