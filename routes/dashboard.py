from datetime import datetime, timedelta
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from extensions import db
from models import Customer, Service, Notification, CustomService
from utils.bihar_services import by_category as bihar_by_category

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def index():
    user_id = current_user.id
    today = datetime.utcnow().date()

    total_customers = Customer.query.filter_by(user_id=user_id).count()

    services_q = Service.query.join(Customer).filter(Customer.user_id == user_id)
    pending = services_q.filter(Service.status != "Completed").count()
    completed = services_q.filter(Service.status == "Completed").count()

    today_earnings = db.session.query(func.coalesce(func.sum(Service.amount), 0.0)).join(Customer).filter(
        Customer.user_id == user_id,
        Service.status == "Completed",
        func.date(Service.completion_date) == today,
    ).scalar() or 0.0

    # Daily revenue last 7 days
    daily_labels, daily_values = [], []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        v = db.session.query(func.coalesce(func.sum(Service.amount), 0.0)).join(Customer).filter(
            Customer.user_id == user_id,
            Service.status == "Completed",
            func.date(Service.completion_date) == d,
        ).scalar() or 0.0
        daily_labels.append(d.strftime("%d %b"))
        daily_values.append(float(v))

    # Monthly revenue (last 6 months)
    monthly_labels, monthly_values = [], []
    for i in range(5, -1, -1):
        month_start = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        v = db.session.query(func.coalesce(func.sum(Service.amount), 0.0)).join(Customer).filter(
            Customer.user_id == user_id,
            Service.status == "Completed",
            Service.completion_date >= month_start,
            Service.completion_date < next_month,
        ).scalar() or 0.0
        monthly_labels.append(month_start.strftime("%b %Y"))
        monthly_values.append(float(v))

    # Service breakdown
    breakdown = db.session.query(Service.service_type, func.count(Service.id)).join(Customer).filter(
        Customer.user_id == user_id
    ).group_by(Service.service_type).all()
    bd_labels = [b[0] for b in breakdown] or ["No data"]
    bd_values = [b[1] for b in breakdown] or [1]

    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(5).all()

    custom_items = [
        {"key": f"c{cs.id}", "name_en": cs.name_en, "name_hi": cs.name_hi or cs.name_en,
         "cat": cs.category or "Custom", "emoji": cs.emoji or "🛠️", "fee": cs.fee or 0}
        for cs in CustomService.query.filter_by(user_id=user_id, is_active=True)
                                       .order_by(CustomService.created_at.desc()).all()
    ]
    groups = list(bihar_by_category())
    if custom_items:
        groups.insert(0, ("My Services", custom_items))

    sub = current_user.subscription
    is_premium = bool(sub and (sub.plan_name or "").lower().startswith("premium")
                      and sub.is_active and sub.days_left > 0)

    return render_template(
        "dashboard/index.html",
        total_customers=total_customers,
        pending=pending,
        completed=completed,
        today_earnings=today_earnings,
        daily_labels=daily_labels,
        daily_values=daily_values,
        monthly_labels=monthly_labels,
        monthly_values=monthly_values,
        bd_labels=bd_labels,
        bd_values=bd_values,
        notifications=notifications,
        subscription=sub,
        is_premium=is_premium,
        bihar_groups=groups,
    )
