from datetime import datetime
from extensions import db


class CustomerDocument(db.Model):
    """A document the customer sent to the operator via the QR handoff.

    Files are stored on disk under uploads/customer_<id>/ and only the
    operator who owns the customer can download them.
    """
    __tablename__ = "customer_documents"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    stored_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(120))
    size_bytes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
