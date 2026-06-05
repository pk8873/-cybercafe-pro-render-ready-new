from datetime import datetime
from extensions import db


class PremiumPayment(db.Model):
    __tablename__ = "premium_payments"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    plan_name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    duration_days = db.Column(db.Integer, default=30)
    txn_ref = db.Column(db.String(120), nullable=False)
    payer_note = db.Column(db.String(255))
    status = db.Column(db.String(20), default="pending")  # pending|approved|rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)

    user = db.relationship("User", backref=db.backref("premium_payments", lazy=True, cascade="all, delete-orphan"))
