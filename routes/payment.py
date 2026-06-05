from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from extensions import db
from models import Payment, Service, Customer

payment_bp = Blueprint("payment", __name__)

METHODS = ["Cash", "UPI", "Card", "Bank Transfer", "Wallet", "Other"]


@payment_bp.route("/payments")
@login_required
def list_payments():
    method = request.args.get("method", "").strip()
    q = Payment.query.filter_by(user_id=current_user.id)
    if method:
        q = q.filter(Payment.method == method)
    payments = q.order_by(Payment.created_at.desc()).all()
    total = sum(p.amount for p in payments)
    by_method = (
        db.session.query(Payment.method, func.coalesce(func.sum(Payment.amount), 0))
        .filter(Payment.user_id == current_user.id)
        .group_by(Payment.method).all()
    )
    services = {s.id: s for s in Service.query.join(Customer).filter(Customer.user_id == current_user.id).all()}
    return render_template("payment/list.html",
                           payments=payments, total=total, methods=METHODS,
                           method=method, by_method=by_method, services=services)


@payment_bp.route("/payments/new", methods=["GET", "POST"])
@login_required
def create():
    services = Service.query.join(Customer).filter(Customer.user_id == current_user.id).order_by(Service.submission_date.desc()).all()
    if request.method == "POST":
        try:
            amount = float(request.form.get("amount") or 0)
        except ValueError:
            amount = 0
        method = (request.form.get("method") or "Cash").strip()
        sid = request.form.get("service_id") or None
        if amount <= 0:
            flash("Enter a valid amount.", "danger")
            return render_template("payment/form.html", services=services, methods=METHODS)
        if method not in METHODS:
            method = "Cash"
        service = None
        if sid:
            service = Service.query.get(int(sid))
            if not service or service.customer.user_id != current_user.id:
                abort(403)
        p = Payment(user_id=current_user.id, service_id=service.id if service else None,
                    amount=amount, method=method, created_at=datetime.utcnow())
        db.session.add(p); db.session.commit()
        flash(f"Payment of ₹{amount:.2f} recorded via {method}.", "success")
        return redirect(url_for("payment.list_payments"))
    return render_template("payment/form.html", services=services, methods=METHODS)


@payment_bp.route("/payments/<int:pid>/delete", methods=["POST"])
@login_required
def delete(pid):
    p = Payment.query.get_or_404(pid)
    if p.user_id != current_user.id:
        abort(403)
    db.session.delete(p); db.session.commit()
    flash("Payment removed.", "info")
    return redirect(url_for("payment.list_payments"))
