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

@app.route("/")
@login_required
def home():
    memory = psutil.virtual_memory()
    ram_usage = f"{memory.used // (1024 * 1024)} MB von {memory.total // (1024 * 1024)} MB"
    return render_template("dashboard/dashboard.html", ram_usage=ram_usage, user=current_user)

@app.route("/account-management")
@login_required
def account_management():
    return render_template("account/account_management.html", user=current_user)

@app.route("/my_payments", methods=["GET"])
@login_required
def my_payments():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.paid_at.desc()).all()
    return render_template("payments/my_payments.html", orders=orders, user=current_user)

@app.route("/help")
@login_required
def help_page():
    return render_template("help/help.html", user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Du wurdest erfolgreich ausgeloggt.", "info")
    return redirect(url_for("login"))

@app.route("/support")
@login_required
def support():
    return render_template("support.html", user=current_user)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)
