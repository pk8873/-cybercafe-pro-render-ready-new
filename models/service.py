from datetime import datetime
from extensions import db


class Service(db.Model):
    __tablename__ = "services"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(30), default="Pending")  # Pending / In Progress / Completed
    amount = db.Column(db.Float, default=0.0)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    completion_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
