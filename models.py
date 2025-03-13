from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Enum, String, Integer, Float, Boolean, DateTime, ForeignKey
import json

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(100), unique=True, nullable=False)
    password_hash = db.Column(String(200), nullable=False)
    is_admin = db.Column(Boolean, default=False)
    subscription = db.Column(String(50), default="free")

    linked_accounts = db.Column(db.Text, default="[]")  # Linked Accounts als JSON-String

    orders = db.relationship("Order", backref="user", lazy=True)
    signal_providers = db.relationship("SignalProvider", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_linked_accounts(self):
        return json.loads(self.linked_accounts or "[]")

    def set_linked_accounts(self, accounts):
        self.linked_accounts = json.dumps(accounts)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription = db.Column(String(50), nullable=False)
    price = db.Column(Float, nullable=False)
    status = db.Column(Enum("unpaid", "pending", "paid", name="order_status"), default="unpaid")
    paid_at = db.Column(DateTime, nullable=True)
    expires_at = db.Column(DateTime, nullable=True)

    def set_expiry_date(self):
        """ Setzt das Ablaufdatum basierend auf dem Abo-Typ """
        if self.paid_at is None:
            return  

        expiry_map = {
            "monthly": timedelta(days=30),
            "quarterly": timedelta(days=90),
            "yearly": timedelta(days=365),
            "lifetime": timedelta(days=365 * 100)  # 100 Jahre als Ersatz für unbegrenzt
        }

        self.expires_at = self.paid_at + expiry_map.get(self.subscription, None) if self.subscription in expiry_map else None


class SignalProvider(db.Model):
    __tablename__ = "signal_providers"

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_name = db.Column(String(100), nullable=False)
    
    # Risikomanagement
    risk_mode = db.Column(String(50), default="fixed_lot")  # "fixed_lot", "percentage", etc.
    risk_value = db.Column(Float, default=0.01)  # 0.01 Lot oder 1% Risiko

    # Take-Profit Strategien
    tp_strategy = db.Column(String(100), default="default")  # "Move SL to Entry on TP1"

    created_at = db.Column(DateTime, default=datetime.utcnow)
