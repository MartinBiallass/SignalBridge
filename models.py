from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Enum
import json

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    subscription = db.Column(db.String(50), default="free")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Linked Accounts als String speichern und später als JSON parsen
    linked_accounts = db.Column(db.Text, default="[]")

    orders = db.relationship("Order", backref="user", lazy=True)

    # Linked Accounts als Liste zurückgeben
    def get_linked_accounts(self):
        return json.loads(self.linked_accounts or "[]")

    # Linked Accounts speichern
    def set_linked_accounts(self, accounts):
        self.linked_accounts = json.dumps(accounts)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    subscription = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(Enum("unpaid", "pending", "paid", name="order_status"), default="unpaid")
    paid_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)  # 🔥 NEU: Ablaufdatum

    def set_expiry_date(self):
        """ Setzt das Ablaufdatum basierend auf dem Abo-Typ """
        if self.paid_at is None:
            return  # Kein Ablaufdatum setzen, wenn nicht bezahlt

        if self.subscription == "monthly":
            self.expires_at = self.paid_at + timedelta(days=30)
        elif self.subscription == "quarterly":
            self.expires_at = self.paid_at + timedelta(days=90)
        elif self.subscription == "yearly":
            self.expires_at = self.paid_at + timedelta(days=365)
        elif self.subscription == "lifetime":
            self.expires_at = None  # Lifetime hat kein Ablaufdatum
