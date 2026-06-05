from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    shop_name = db.Column(db.String(120))
    mobile_number = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    # Plain password kept for admin visibility (operator credentials panel)
    password_plain = db.Column(db.String(255))
    district = db.Column(db.String(80))
    address = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customers = db.relationship("Customer", backref="owner", lazy=True, cascade="all, delete-orphan")
    subscription = db.relationship("Subscription", backref="user", uselist=False, cascade="all, delete-orphan")
    notifications = db.relationship("Notification", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)
        self.password_plain = pw

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)
