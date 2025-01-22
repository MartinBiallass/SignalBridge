from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import psutil
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Sprachkonfigurationen
translations = {
    "de": {
        "home": "Startseite",
        "account_management": "Kontoverwaltung",
        "message_history": "Nachrichtenverlauf",
        "support": "Support",
        "help": "Hilfe",
        "welcome": "Willkommen bei SignalBridge",
        "membership": "Mitgliedschaftsdauer",
        "accounts_used": "Genutzte Konten",
        "system_cockpit": "System Cockpit",
    },
    "en": {
        "home": "Home Page",
        "account_management": "Account Management",
        "message_history": "Message History",
        "support": "Support",
        "help": "Help",
        "welcome": "Welcome to SignalBridge",
        "membership": "Membership Duration",
        "accounts_used": "Accounts Used",
        "system_cockpit": "System Cockpit",
    }
}

start_time = datetime.now()

@app.route("/")
def home():
    lang = session.get("language", "de")
    telegram_account = "test_telegram_user"  # Platzhalter
    connected_accounts = [
        {"name": "MT4", "status": "aktiviert"},
        {"name": "MT5", "status": "deaktiviert"}
    ]

    # System Cockpit Daten
    memory = psutil.virtual_memory()
    ram_usage = f"{memory.used // (1024 * 1024)} MB von {memory.total // (1024 * 1024)} MB"

    return render_template(
        "home.html",
        lang=lang,
        translations=translations[lang],
        telegram_account=telegram_account,
        connected_accounts=connected_accounts,
        ram_usage=ram_usage
    )

@app.route('/account-management')
def account_management():
    signal_providers = [
        {"name": "BEST GOLD SIGNAL", "pips": 149.90, "win_loss": 100, "profit": 29.80, "gain": 0.50},
        {"name": "Forex Pros", "pips": 1455.90, "win_loss": 57, "profit": 265.25, "gain": 4.42},
        {"name": "Trading Lions", "pips": -50.70, "win_loss": 77, "profit": -10.00, "gain": -1.42},
    ]
    return render_template("account_management.html", signal_providers=signal_providers)

@app.route('/edit-signal', methods=['GET', 'POST'])
def edit_signal():
    if request.method == 'POST':
        # Handle POST data here if needed
        data = request.form
        print("Risk Management Data:", data)
        return "Data received", 200
    return render_template('edit_signal.html')

@app.route('/take-profit-levels', methods=['POST'])
def take_profit_levels():
    tp_levels = request.json.get("tp_levels", [])
    print("Received TP Levels:", tp_levels)
    return jsonify({"message": "Take Profit Levels updated successfully!"})

@app.route('/message-history')
def message_history():
    messages = [
        {"timestamp": "2025-01-21 14:30", "signal": "EUR/USD", "provider": "BEST GOLD SIGNAL"},
        {"timestamp": "2025-01-21 14:00", "signal": "GBP/USD", "provider": "Forex Pros"},
        {"timestamp": "2025-01-21 13:30", "signal": "USD/JPY", "provider": "Trading Lions"}
    ]
    return render_template(
        "message_history.html",
        messages=messages
    )

@app.route('/support', methods=["GET", "POST"])
def support():
    if request.method == "POST":
        ticket = request.form.get("ticket_text")
        return "Ticket erstellt!"
    tickets = [
        {"id": 1, "title": "API Fehler", "status": "Offen"},
        {"id": 2, "title": "Telegram Verbindung", "status": "Geschlossen"}
    ]
    return render_template(
        "support.html",
        tickets=tickets
    )

@app.route('/help')
def help():
    tutorials = [
        {"title": "Erste Schritte", "link": "#"},
        {"title": "Signalgeber verwalten", "link": "#"},
        {"title": "System Cockpit", "link": "#"}
    ]
    return render_template(
        "help.html",
        tutorials=tutorials
    )

if __name__ == "__main__":
    app.run(debug=True)
