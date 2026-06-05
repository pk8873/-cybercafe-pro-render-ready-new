from datetime import datetime, timedelta
from urllib.parse import quote
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from extensions import db
from models import PremiumPayment, Subscription

premium_bp = Blueprint("premium", __name__)


PLANS = [
    {"key": "monthly", "name": "Premium Monthly", "amount": 299.0, "days": 30,
     "features": ["Unlimited customers", "Unlimited services", "Priority support", "All advanced features"]},
    {"key": "quarterly", "name": "Premium Quarterly", "amount": 799.0, "days": 90,
     "features": ["Everything in Monthly", "Save ₹98", "Quarterly reports"]},
    {"key": "yearly", "name": "Premium Yearly", "amount": 2499.0, "days": 365,
     "features": ["Everything in Quarterly", "Save ₹1089", "Free onboarding"]},
]


def _plan(key):
    for p in PLANS:
        if p["key"] == key:
            return p
    return None


def _upi_link(amount, note):
    upi_id = current_app.config.get("ADMIN_UPI_ID") or "admin@upi"
    payee = current_app.config.get("ADMIN_UPI_NAME") or "CyberCafe ERP"
    return (
        f"upi://pay?pa={quote(upi_id)}&pn={quote(payee)}"
        f"&am={amount:.2f}&cu=INR&tn={quote(note)}"
    )


@premium_bp.route("/premium")
@login_required
def plans():
    upi_id = current_app.config.get("ADMIN_UPI_ID") or "admin@upi"
    payee = current_app.config.get("ADMIN_UPI_NAME") or "CyberCafe ERP"
    return render_template("premium/plans.html", plans=PLANS, upi_id=upi_id, payee=payee)


@premium_bp.route("/premium/buy/<plan_key>", methods=["GET", "POST"])
@login_required
def buy(plan_key):
    plan = _plan(plan_key)
    if not plan:
        flash("Invalid plan.", "danger")
        return redirect(url_for("premium.plans"))

    note = f"PREMIUM-{plan['key'].upper()}-U{current_user.id}"
    upi_link = _upi_link(plan["amount"], note)
    upi_id = current_app.config.get("ADMIN_UPI_ID") or "admin@upi"
    payee = current_app.config.get("ADMIN_UPI_NAME") or "CyberCafe ERP"

    if request.method == "POST":
        txn_ref = (request.form.get("txn_ref") or "").strip()
        payer_note = (request.form.get("payer_note") or "").strip()
        if len(txn_ref) < 6:
            flash("Enter a valid transaction reference (UPI/UTR number).", "danger")
        else:
            pay = PremiumPayment(
                user_id=current_user.id,
                plan_name=plan["name"],
                amount=plan["amount"],
                duration_days=plan["days"],
                txn_ref=txn_ref,
                payer_note=payer_note,
                status="pending",
            )
            db.session.add(pay)
            db.session.commit()
            flash("Payment submitted. We will activate your premium plan after verification.", "success")
            return redirect(url_for("premium.my_payments"))

    return render_template("premium/buy.html", plan=plan, upi_link=upi_link,
                           upi_id=upi_id, payee=payee, note=note)


@premium_bp.route("/premium/my")
@login_required
def my_payments():
    payments = (PremiumPayment.query
                .filter_by(user_id=current_user.id)
                .order_by(PremiumPayment.created_at.desc()).all())
    return render_template("premium/my.html", payments=payments,
                           subscription=current_user.subscription)


# ---- Admin actions (mounted under admin blueprint paths but kept here for cohesion) ----

from functools import wraps
from flask import abort
from models import User


def _admin_required(f):
    @wraps(f)
    def w(*a, **kw):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(404)
        return f(*a, **kw)
    return w


@premium_bp.route("/secure-admin-dashboard/premium-payments")
@_admin_required
def admin_list():
    status = request.args.get("status", "").strip()
    q = PremiumPayment.query
    if status in ("pending", "approved", "rejected"):
        q = q.filter_by(status=status)
    payments = q.order_by(PremiumPayment.created_at.desc()).all()
    return render_template("admin/premium_payments.html", payments=payments, status=status)


@premium_bp.route("/secure-admin-dashboard/premium-payments/<int:pid>/<action>", methods=["POST"])
@_admin_required
def admin_action(pid, action):
    p = PremiumPayment.query.get_or_404(pid)
    if action == "approve" and p.status != "approved":
        p.status = "approved"
        p.reviewed_at = datetime.utcnow()
        # Upgrade user's subscription
        sub = p.user.subscription
        if not sub:
            sub = Subscription(user_id=p.user_id)
            db.session.add(sub)
        base = max(sub.expiry_date or datetime.utcnow(), datetime.utcnow())
        sub.plan_name = p.plan_name
        sub.start_date = datetime.utcnow()
        sub.expiry_date = base + timedelta(days=p.duration_days)
        sub.is_active = True
        db.session.commit()
        flash(f"Approved ₹{p.amount:.2f} from {p.user.email}. Subscription extended.", "success")
    elif action == "reject" and p.status != "rejected":
        p.status = "rejected"
        p.reviewed_at = datetime.utcnow()
        db.session.commit()
        flash("Payment marked as rejected.", "info")
    return redirect(url_for("premium.admin_list"))
