from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from extensions import db
from models import Service, Customer
from utils.forms import ServiceForm

service_bp = Blueprint("service", __name__)


def _customers_choices():
    return [(c.id, c.full_name) for c in Customer.query.filter_by(user_id=current_user.id).order_by(Customer.full_name).all()]


def _own_service(s):
    if s.customer.user_id != current_user.id:
        abort(403)


@service_bp.route("/services")
@login_required
def list_services():
    status = request.args.get("status", "").strip()
    q = Service.query.join(Customer).filter(Customer.user_id == current_user.id)
    if status:
        q = q.filter(Service.status == status)
    services = q.order_by(Service.submission_date.desc()).all()
    return render_template("service/list.html", services=services, status=status)


@service_bp.route("/services/new", methods=["GET", "POST"])
@login_required
def create():
    form = ServiceForm()
    # Pre-fill from quick-grid links: /services/new?type=Aay&amount=50
    if request.method == "GET":
        t = request.args.get("type")
        a = request.args.get("amount")
        if t:
            form.service_type.data = t
        if a:
            try:
                form.amount.data = float(a)
            except ValueError:
                pass
    form.customer_id.choices = _customers_choices()
    if not form.customer_id.choices:
        flash("Add a customer first.", "warning")
        return redirect(url_for("customer.create"))
    if form.validate_on_submit():
        s = Service(
            customer_id=form.customer_id.data,
            service_type=form.service_type.data,
            status=form.status.data,
            amount=form.amount.data or 0.0,
            notes=form.notes.data,
        )
        if s.status == "Completed":
            s.completion_date = datetime.utcnow()
        db.session.add(s); db.session.commit()
        flash("Service added.", "success")
        return redirect(url_for("service.list_services"))
    return render_template("service/form.html", form=form, title="New Service")


@service_bp.route("/services/<int:sid>/edit", methods=["GET", "POST"])
@login_required
def edit(sid):
    s = Service.query.get_or_404(sid); _own_service(s)
    form = ServiceForm(obj=s)
    form.customer_id.choices = _customers_choices()
    if form.validate_on_submit():
        prev = s.status
        form.populate_obj(s)
        s.amount = form.amount.data or 0.0
        if s.status == "Completed" and prev != "Completed":
            s.completion_date = datetime.utcnow()
        db.session.commit()
        flash("Service updated.", "success")
        return redirect(url_for("service.list_services"))
    return render_template("service/form.html", form=form, title="Edit Service")


@service_bp.route("/services/<int:sid>/delete", methods=["POST"])
@login_required
def delete(sid):
    s = Service.query.get_or_404(sid); _own_service(s)
    db.session.delete(s); db.session.commit()
    flash("Service deleted.", "info")
    return redirect(url_for("service.list_services"))
