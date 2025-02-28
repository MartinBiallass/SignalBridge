import os
import psutil
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from models import db, User, Order
from flask_login import login_required
from flask_apscheduler import APScheduler


def calculate_price(subscription):
    price_map = {
        "monthly": 19.90,
        "quarterly": 49.90,
        "yearly": 169.90
    }
    return price_map.get(subscription, 19.90)  # Standard: 19.90€

# Flask App initialisieren
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Scheduler initialisieren
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

def check_expiring_subscriptions():
    """ Überprüft alle Abos, die in den nächsten 3 Tagen auslaufen. """
    today = datetime.utcnow()
    warning_days = [1, 2, 3]  # 3, 2, 1 Tage vor Ablauf

    expiring_orders = Order.query.filter(
        Order.expires_at.isnot(None),
        Order.expires_at - today <= timedelta(days=3),  # Alle Abos, die in den nächsten 3 Tagen auslaufen
        Order.status == "paid"
    ).all()

    for order in expiring_orders:
        days_left = (order.expires_at - today).days
        if days_left in warning_days:
            flash(f"⚠️ Dein Abo ({order.subscription}) läuft in {days_left} Tagen aus! Bitte verlängern.", "warning")
            print(f"🔔 Erinnerung: Nutzer {order.user.username} soll gewarnt werden (Abo läuft in {days_left} Tagen ab).")

# Scheduler-Job einrichten: Die Funktion soll **einmal pro Tag** laufen.
scheduler.add_job(
    id="check_subscriptions",
    func=check_expiring_subscriptions,
    trigger="interval",
    hours=24
)

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
    # Überprüfen, ob ein Admin auf sein normales Dashboard will
    if current_user.is_admin and request.args.get("admin_view") != "false":
        return redirect(url_for("admin_dashboard"))  # Standardmäßige Umleitung

    # Normales User-Dashboard laden
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

    # Neuen User erstellen
    new_user = User(username=username, subscription=subscription)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    # 🔥 Direkt nach der Registrierung einloggen!
    login_user(new_user, remember=True)
    session["user_id"] = new_user.id  # Explizit die User-ID setzen

    print(f"✅ Neuer Nutzer registriert: {new_user.username}, ID: {new_user.id}")

    flash("✅ Registrierung erfolgreich! Bitte zahle dein Abo.", "success")
    return redirect(url_for("my_payments"))  # Weiterleitung zur Zahlungsseite


@app.route("/account-management")
@login_required
def account_management():
    return render_template("account/account_management.html", user=current_user)

# -------Admin dashboard---
@app.route("/admin")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("⚠️ Zugriff verweigert. Du bist kein Admin!", "danger")
        return redirect(url_for("dashboard"))

    users = User.query.all()
    orders = Order.query.all()
    
    return render_template("admin/admin_dashboard.html", users=users, orders=orders)

@app.route("/approve_order/<int:order_id>", methods=["POST"])
@login_required
def approve_order(order_id):
    if not current_user.is_admin:
        flash("❌ Zugriff verweigert!", "danger")
        return redirect(url_for("dashboard"))

    order = Order.query.get(order_id)
    if not order:
        flash("❌ Bestellung nicht gefunden!", "danger")
        return redirect(url_for("admin_dashboard"))

    order.status = "paid"
    order.paid_at = datetime.utcnow()
    db.session.commit()

    flash(f"✅ Bestellung {order.id} wurde erfolgreich genehmigt!", "success")
    return redirect(url_for("admin_dashboard"))

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

#-----admin checklist----
@app.route("/check_subscriptions", methods=["GET"])
@login_required
def check_subscriptions():
    """Manuelle Überprüfung der auslaufenden Abos"""
    if not current_user.is_admin:
        flash("🚫 Zugriff verweigert! Nur für Admins.", "danger")
        return redirect(url_for("dashboard"))

    today = datetime.utcnow()
    warning_days = [1, 2, 3]  # Warnungen 3, 2, 1 Tage vor Ablauf

    expiring_orders = Order.query.filter(
        Order.expires_at.isnot(None),
        Order.expires_at - today <= timedelta(days=3),
        Order.status == "paid"
    ).all()

    expiring_list = []
    for order in expiring_orders:
        days_left = (order.expires_at - today).days
        if days_left in warning_days:
            expiring_list.append({
                "username": order.user.username,
                "subscription": order.subscription,
                "expires_in": days_left
            })

    return render_template("admin/check_subscriptions.html", expiring_list=expiring_list)


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
        # Überprüfe, welches Abo der Nutzer gewählt hat
        subscription = current_user.subscription if current_user.subscription else "Standard"

        # Bestimme die Laufzeit basierend auf dem Abo
        duration_map = {
            "monthly": 30,   # 1 Monat
            "quarterly": 90, # 3 Monate
            "yearly": 365    # 1 Jahr
        }
        duration_days = duration_map.get(subscription, 30)  # Standard: 30 Tage

        # Überprüfe, ob bereits eine offene Bestellung existiert
        order = Order.query.filter_by(user_id=current_user.id, status="pending").first()

        if not order:
            # Falls keine Bestellung existiert, erstelle eine neue mit Ablaufdatum
            order = Order(
                user_id=current_user.id,
                subscription=subscription,
                price=calculate_price(subscription),  # Berechne Preis dynamisch
                status="paid",
                paid_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=duration_days)  # Ablaufdatum setzen
            )
            db.session.add(order)
        else:
            # Falls bereits eine Bestellung existiert, aktualisieren wir nur die Daten
            order.status = "paid"
            order.paid_at = datetime.utcnow()
            order.expires_at = datetime.utcnow() + timedelta(days=duration_days)  # Ablaufdatum setzen

        # Datenbank-Änderungen speichern
        db.session.commit()

        print(f"✅ Zahlung erfolgreich: {current_user.username}, Abo: {subscription}, Preis: {order.price}€, Läuft ab am: {order.expires_at}")

        flash(f"✅ Zahlung mit {payment_method} erfolgreich! Dein Abo läuft bis {order.expires_at}.", "success")
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

# --------- Log in / Log Out ----------
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

            print(f"🔍 DEBUG: Eingeloggter User -> ID: {user.id}, Name: {user.username}")
            print(f"🔍 DEBUG: current_user -> ID: {current_user.id if current_user else 'None'}")

            flash("✅ Login erfolgreich!", "success")
            
            # Hier war dein Fehler – jetzt korrekt eingerückt:
            if user.is_admin:  
                return redirect(url_for("admin_dashboard"))

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

from flask_apscheduler import APScheduler

scheduler = APScheduler()

def check_subscription_expiry():
    with app.app_context():
        expiring_orders = Order.query.filter(
            Order.expires_at <= datetime.utcnow() + timedelta(days=3),
            Order.status == "paid"
        ).all()

        for order in expiring_orders:
            days_left = (order.expires_at - datetime.utcnow()).days
            if days_left == 3:
                flash(f"⏳ Dein Abo läuft in 3 Tagen aus. Verlängere es jetzt!", "warning")
            elif days_left == 2:
                flash(f"⚠️ Dein Abo läuft in 2 Tagen aus. Verlängere es jetzt!", "warning")
            elif days_left == 1:
                flash(f"🚨 Dein Abo läuft MORGEN aus! Bitte verlängere es sofort.", "danger")

scheduler.add_job(id="subscription_checker", func=check_subscription_expiry, trigger="interval", hours=24)
scheduler.start()

# Flask-App starten
socketio.run(app, host="0.0.0.0", port=5001, debug=True)
