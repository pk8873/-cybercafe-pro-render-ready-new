from datetime import datetime
from extensions import db


class CustomService(db.Model):
    """Per-operator custom service entry with editable price.

    Lets each operator add their own service offerings (or override price)
    that appear in the dashboard quick-grid alongside the built-in
    Bihar services.
    """

    __tablename__ = "custom_services"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name_en = db.Column(db.String(120), nullable=False)
    name_hi = db.Column(db.String(120))
    category = db.Column(db.String(60), default="Custom")
    emoji = db.Column(db.String(8), default="🛠️")
    fee = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
