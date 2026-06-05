from datetime import datetime, timedelta
from extensions import db


class Subscription(db.Model):
    __tablename__ = "subscriptions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    plan_name = db.Column(db.String(50), default="Free Trial")
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=14))
    is_active = db.Column(db.Boolean, default=True)

    @property
    def days_left(self):
        delta = self.expiry_date - datetime.utcnow()
        return max(delta.days, 0)
