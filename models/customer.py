from datetime import datetime
from extensions import db


class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    mobile_number = db.Column(db.String(20))
    aadhaar_last_4 = db.Column(db.String(4))
    address = db.Column(db.String(255))
    village = db.Column(db.String(120))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    services = db.relationship(
        "Service", backref="customer", lazy=True, cascade="all, delete-orphan"
    )
    documents = db.relationship(
        "CustomerDocument",
        backref="customer",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="CustomerDocument.created_at.desc()",
    )
