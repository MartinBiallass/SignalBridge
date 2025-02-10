import os
import psutil
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from models import db, User, Order  # Importiere Modelle aus `models.py`

# **📌 Absoluter Pfad zur Datenbank**
basedir = os.path.abspath(os.path.dirname(__file__))

# **🚀 Flask & WebSocket Initialisierung**
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# **⚙️ Konfiguration**
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'instance', 'database.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# **📂 Sicherstellen, dass `instance/`-Ordner existiert**
if not os.path.exists(os.path.join(basedir, "instance")):
    os.makedirs(os.path.join(basedir, "instance"))

# **🔧 Initialisierung von Datenbank, Session und Migrations**
db.init_app(app)
migrate = Migrate(app, db)
Session(app)

# **🔑 Login-Manager einrichten**
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# **🏠 Startseite**
@app.route("/")
@login_required
def home():
    memory = psutil.virtual_memory()
    ram_usage = f"{memory.used // (1024 * 1024)} MB von {memory.total // (1024 * 1024)} MB"

    # **Falls der User nicht bezahlt hat, Weiterleitung zur Mock-Zahlung**
    if not current_user.is_admin:
        order = Order.query.filter_by(user_id=current_user.id).first()
        if order and order.status == "unpaid":
            return redirect(url_for("mock_payment"))

    return render_template("dashboard/dashboard.html", ram_usage=ram_usage, user=current_user)

# **🔓 Benutzer-Login**
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
    
    return render_template("account/login.html")

# **📝 Benutzer-Registrierung mit Abo-Auswahl**
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        subscription = request.form.get("subscription", "free")
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        # **Prüfen, ob Benutzername existiert**
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Fehler: Benutzername existiert bereits!", 400

        # **Neuen Benutzer & Bestellung anlegen**
        new_user = User(username=username, password=hashed_password, subscription=subscription)
        db.session.add(new_user)
        db.session.commit()

        new_order = Order(user_id=new_user.id, subscription=subscription, price=49.90, status="unpaid")
        db.session.add(new_order)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("mock_payment"))
    
    return render_template("account/register.html")

# **🚪 Benutzer-Logout**
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

# **💳 Mock-Zahlungsseite**
@app.route("/mock-payment", methods=["GET", "POST"])
@login_required
def mock_payment():
    order = Order.query.filter_by(user_id=current_user.id).first()

    # **Falls keine Bestellung existiert, erstelle eine mit Standardwerten**
    if not order:
        order = Order(user_id=current_user.id, subscription="Quartal", price=49.90, status="unpaid")
        db.session.add(order)
        db.session.commit()

    if request.method == "POST":
        if order and order.status == "unpaid":
            order.status = "paid"
            db.session.commit()
            return redirect(url_for("home"))

    return render_template("payments/mock_payment.html", order=order)

# **📡 WebSocket für Echtzeit-Updates**
@socketio.on("new_trade")
def handle_new_trade(data):
    emit("update_trades", data, broadcast=True)

# **📌 Datenbank erstellen, falls nicht vorhanden**
with app.app_context():
    db.create_all()

# **🚀 Flask-App starten**
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)
