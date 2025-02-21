import os
import psutil
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from models import db, User, Order
from flask_login import login_required

# Flask App initialisieren
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Flask-Konfiguration
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'instance', 'database.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Erstelle Instanz-Verzeichnis falls nicht vorhanden
if not os.path.exists(os.path.join(basedir, "instance")):
    os.makedirs(os.path.join(basedir, "instance"))

# Initialisiere Datenbank
db.init_app(app)
migrate = Migrate(app, db)
Session(app)

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------- Dashboard ------------
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard/dashboard.html", user=current_user)


# ------------- Löschen von Accounts
@app.route("/")
def landing_page():
    return render_template("index.html")


#-------- Registrierung--------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username")
    password = request.form.get("password")
    subscription = request.form.get("subscription")

    if not username or not password or not subscription:
        flash("⚠️ Bitte alle Felder ausfüllen!", "danger")
        return redirect(url_for("register"))

    if User.query.filter_by(username=username).first():
        flash("❌ Benutzername existiert bereits.", "danger")
        return redirect(url_for("register"))

    # User mit Passwort-Hash erstellen
    new_user = User(username=username, subscription=subscription)
    new_user.set_password(password)  # ✅ Hier wird das Passwort richtig gespeichert

    db.session.add(new_user)
    db.session.commit()

    # Debug-Print prüfen, ob User gespeichert wurde
    print(f"✅ Neuer Nutzer registriert: {new_user.username}, ID: {new_user.id}")

    flash("✅ Registrierung erfolgreich! Bitte zahle dein Abo.", "success")
    return redirect(url_for("my_payments"))


@app.route("/account-management")
@login_required
def account_management():
    return render_template("account/account_management.html", user=current_user)

# -------Admin dashboard---
@app.route("/admin", methods=["GET"])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("🚫 Zugriff verweigert! Nur für Admins.", "danger")
        return redirect(url_for("landing_page"))
    
    # Hole alle Benutzer und Bestellungen
    users = User.query.all()
    orders = Order.query.all()

    return render_template("admin/dashboard.html", users=users, orders=orders)

# ----admin Aktion--Nutzer löschen-----
@app.route("/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash("🚫 Zugriff verweigert!", "danger")
        return redirect(url_for("landing_page"))

    user = User.query.get(user_id)
    if user.username == "admin":
        flash("⚠️ Der Admin-Account kann nicht gelöscht werden!", "danger")
        return redirect(url_for("admin_dashboard"))

    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f"✅ Benutzer {user.username} gelöscht!", "success")
    else:
        flash("❌ Benutzer nicht gefunden!", "danger")

    return redirect(url_for("admin_dashboard"))

@app.route("/my_payments", methods=["GET"])
@login_required
def my_payments():
    db.session.refresh(current_user)  # Erzwingt das Neuladen des Benutzers
    user = User.query.get(current_user.id)  # Holt den aktuellen Benutzer korrekt
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.paid_at.desc()).all()
    return render_template("payments/my_payments.html", orders=orders, user=user)

# -----Mock Payment-------
@app.route("/mock_payment", methods=["POST"])
@login_required
def mock_payment():
    payment_method = request.form.get("payment_method")

    if payment_method:
        # Überprüfe, ob der Nutzer bereits ein Abo gewählt hat
        subscription = current_user.subscription if current_user.subscription else "Standard"

        # Überprüfe, ob bereits eine offene Bestellung existiert
        order = Order.query.filter_by(user_id=current_user.id, status="pending").first()

        if not order:
            # Falls keine Bestellung existiert, erstelle eine neue mit der `subscription`
            order = Order(
                user_id=current_user.id,
                subscription=subscription,  # 🔥 Füge das fehlende Feld hinzu!
                price=9.99,  # Hier evtl. den richtigen Preis aus einer Preistabelle abrufen
                status="active",
                paid_at=datetime.utcnow()
            )
            db.session.add(order)
        else:
            # Falls bereits eine Bestellung existiert, setzen wir den Status auf aktiv
            order.status = "active"
            order.paid_at = datetime.utcnow()

        # Datenbank-Änderungen speichern
        db.session.commit()

        # Debug-Ausgabe zum Überprüfen
        print(f"✅ Zahlung erfolgreich: {current_user.username}, Abo: {subscription}, Preis: {order.price}€")

        flash(f"✅ Zahlung mit {payment_method} erfolgreich! Dein Zugang ist jetzt aktiv.", "success")
    else:
        flash("⚠️ Bitte eine Zahlungsmethode wählen!", "danger")

    return redirect(url_for("dashboard"))



@app.route("/linked_accounts", methods=["GET", "POST"])
@login_required
def linked_accounts():
    if request.method == "POST":
        new_account = request.form.get("new_account")
        trade_type = request.form.get("trade_type")

        if new_account and trade_type:
            # Neuen Account als Dictionary speichern
            account_info = {"account_name": new_account, "trade_type": trade_type}
            current_user.linked_accounts.append(account_info)
            db.session.commit()
            flash(f"Account {new_account} mit Trade-Typ {trade_type} hinzugefügt!", "success")
        else:
            flash("Bitte alle Felder ausfüllen!", "danger")

    return render_template("account/linked_accounts.html", user=current_user)

# ---------------- Risikomanagement für Trades ----------------

@app.route("/manage_trade/<int:trade_id>", methods=["POST"])
@login_required
def manage_trade(trade_id):
    action = request.form.get("action")
    new_sl = request.form.get("new_sl")
    new_tp = request.form.get("new_tp")

    if action == "close":
        flash(f"Trade {trade_id} wurde geschlossen.", "success")
    elif action == "adjust_sl_tp":
        if new_sl and new_tp:
            flash(f"SL/TP für Trade {trade_id} angepasst: SL: {new_sl}, TP: {new_tp}", "info")
        else:
            flash("Bitte sowohl Stop-Loss als auch Take-Profit angeben.", "danger")

    return redirect(url_for("trade_management"))


@app.route("/help")
@login_required
def help_page():
    return render_template("help/help.html", user=current_user)

# ---------Log in / Log Out----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("⚠️ Bitte fülle alle Felder aus!", "danger")
            return redirect(url_for("login"))

        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):  
            session.clear()  # Stelle sicher, dass keine alten Sessions existieren
            login_user(user, remember=True)  # `remember=True` hält die Session länger aktiv
            session["user_id"] = user.id  # Speichere die User-ID explizit in der Session

            flash("✅ Login erfolgreich!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("❌ Ungültige Anmeldedaten.", "danger")

    return render_template("login.html", login_mode=True)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop("user_id", None)  # Entfernt explizit den Benutzer aus der Session
    session.clear()  # Löscht die gesamte Session
    flash("Du wurdest erfolgreich ausgeloggt.", "info")
    return redirect(url_for("landing_page"))


@app.route("/support")
@login_required
def support():
    return render_template("support.html", user=current_user)

@app.route("/dashboard/live_trades")
@login_required
def dashboard_live_trades():
    return render_template("dashboard/live_trades.html", user=current_user)

@app.route("/live_trades")
@login_required
def live_trades():
    # Beispiel-Daten für Live-Optionstrades
    trades = [
        {"id": 1, "type": "Call", "duration": "5 min", "status": "Aktiv"},
        {"id": 2, "type": "Put", "duration": "15 min", "status": "Abgeschlossen"},
        {"id": 3, "type": "Call", "duration": "30 min", "status": "Aktiv"}
    ]
    for trade in trades:
        if trade["type"] == "Call":
            trade["type"] = "Buy"
        elif trade["type"] == "Put":
            trade["type"] = "Sell"
    return jsonify(trades)
    
@app.route("/create_trade", methods=["POST"])
@login_required
def create_trade():
    symbol = request.form.get("symbol")
    trade_type = request.form.get("trade_type")
    volume = request.form.get("volume")
    stop_loss = request.form.get("stop_loss")
    take_profit = request.form.get("take_profit")

    if symbol and trade_type and volume and stop_loss and take_profit:
        new_trade = {
            "symbol": symbol,
            "type": trade_type,
            "volume": float(volume),
            "stop_loss": float(stop_loss),
            "take_profit": float(take_profit)
        }
        # Hier würden wir den Trade in die DB schreiben (später implementieren)
        print(f"Neuer Trade hinzugefügt: {new_trade}")
        flash(f"Trade für {symbol} als {trade_type} hinzugefügt!", "success")
    else:
        flash("Alle Felder müssen ausgefüllt werden!", "danger")

    return redirect(url_for("dashboard_live_trades"))

# ---------------- Tradeverwaltung ----------------

@app.route("/trade_management", methods=["GET"])
@login_required
def trade_management():
    # Beispielhafte Trades - später aus DB
    trades = [
        {"id": 1, "symbol": "EURUSD", "type": "Buy", "volume": 1.0, "sl": 1.0500, "tp": 1.0700},
        {"id": 2, "symbol": "GBPJPY", "type": "Sell", "volume": 2.0, "sl": 154.500, "tp": 152.000},
        {"id": 3, "symbol": "XAUUSD", "type": "Buy", "volume": 0.5, "sl": 1850.00, "tp": 1950.00}
    ]
    return render_template("settings/trade_management.html", trades=trades, user=current_user)

@app.route("/add_new_trade", methods=["POST"])
@login_required
def add_new_trade():
    symbol = request.form.get("symbol")
    trade_type = request.form.get("type")
    volume = request.form.get("volume")
    sl = request.form.get("sl")
    tp = request.form.get("tp")

    if symbol and trade_type and volume and sl and tp:
        flash(f"Neuer Trade hinzugefügt: {symbol} | {trade_type} | Volumen: {volume} | SL: {sl} | TP: {tp}", "success")
    else:
        flash("Bitte alle Felder korrekt ausfüllen!", "danger")

    return redirect(url_for("trade_management"))

@app.route("/edit_trade/<int:trade_id>", methods=["POST"])
@login_required
def edit_trade(trade_id):
    new_tp = request.form.get("new_tp")
    if new_tp:
        flash(f"Take-Profit für Trade {trade_id} auf {new_tp} geändert!", "success")
    else:
        flash("Bitte einen gültigen TP-Wert angeben!", "danger")

    return redirect(url_for("trade_management"))

@app.route("/delete_trade/<int:trade_id>", methods=["POST"])
@login_required
def delete_trade(trade_id):
    flash(f"Trade {trade_id} erfolgreich gelöscht!", "info")
    return redirect(url_for("trade_management"))

# ---------------- Risikomanagement Logik ----------------

@app.route("/risk_management", methods=["GET", "POST"])
@login_required
def risk_management():
    if request.method == "POST":
        trade_id = request.form.get("trade_id")
        risk_type = request.form.get("risk_type")
        value = request.form.get("value")

        if trade_id and risk_type and value:
            flash(f"Risikomanagement für Trade {trade_id} auf {risk_type} mit Wert {value} gesetzt!", "success")
        else:
            flash("Bitte alle Felder korrekt ausfüllen!", "danger")

    trades = [
        {"id": 1, "symbol": "EURUSD", "type": "Buy", "volume": 1.0, "risk": "Fixed Lots", "value": "0.1"},
        {"id": 2, "symbol": "GBPUSD", "type": "Sell", "volume": 2.0, "risk": "Fixed Cash", "value": "100"},
    ]
    return render_template("settings/risk_management.html", trades=trades, user=current_user)


@app.route("/edit_account/<old_account>", methods=["POST"])
@login_required
def edit_account(old_account):
    new_account = request.form.get("new_account")
    for account in current_user.linked_accounts:
        if account["account_name"] == old_account:
            account["account_name"] = new_account
            db.session.commit()
            flash(f"Account {old_account} wurde in {new_account} umbenannt!", "success")
            break
    else:
        flash("Account nicht gefunden.", "danger")
    return redirect(url_for("linked_accounts"))

if __name__ == "__main__":
    # Admin-Benutzer beim Start prüfen/erstellen
    with app.app_context():
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            new_admin = User(username="admin", is_admin=True)
            new_admin.set_password("admin1234")  # Sichereres Passwort im Produktivbetrieb
            db.session.add(new_admin)
            db.session.commit()
            print("👑 Admin-Benutzer wurde erfolgreich erstellt!")
    
    # Flask-App starten
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)
