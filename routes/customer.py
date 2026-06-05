import os
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, abort,
    send_from_directory, current_app,
)
from flask_login import login_required, current_user
from extensions import db
from models import Customer, CustomerDocument
from utils.forms import CustomerForm

customer_bp = Blueprint("customer", __name__)


def _own(c):
    if c.user_id != current_user.id:
        abort(403)


@customer_bp.route("/customers")
@login_required
def list_customers():
    q = request.args.get("q", "").strip()
    query = Customer.query.filter_by(user_id=current_user.id)
    if q:
        like = f"%{q}%"
        query = query.filter((Customer.full_name.ilike(like)) | (Customer.mobile_number.ilike(like)) | (Customer.village.ilike(like)))
    customers = query.order_by(Customer.created_at.desc()).all()
    return render_template("customer/list.html", customers=customers, q=q)


@customer_bp.route("/customers/new", methods=["GET", "POST"])
@login_required
def create():
    form = CustomerForm()
    if form.validate_on_submit():
        c = Customer(user_id=current_user.id)
        form.populate_obj(c)
        db.session.add(c)
        db.session.commit()
        flash("Customer added. Generate a QR below to receive their documents.", "success")
        return redirect(url_for("customer.view", cid=c.id))
    return render_template("customer/form.html", form=form, title="New Customer")


@customer_bp.route("/customers/<int:cid>/edit", methods=["GET", "POST"])
@login_required
def edit(cid):
    c = Customer.query.get_or_404(cid); _own(c)
    form = CustomerForm(obj=c)
    if form.validate_on_submit():
        form.populate_obj(c)
        db.session.commit()
        flash("Customer updated.", "success")
        return redirect(url_for("customer.list_customers"))
    return render_template("customer/form.html", form=form, title="Edit Customer")


@customer_bp.route("/customers/<int:cid>")
@login_required
def view(cid):
    c = Customer.query.get_or_404(cid); _own(c)
    return render_template("customer/view.html", c=c)


@customer_bp.route("/customers/<int:cid>/delete", methods=["POST"])
@login_required
def delete(cid):
    c = Customer.query.get_or_404(cid); _own(c)
    db.session.delete(c); db.session.commit()
    flash("Customer deleted.", "info")
    return redirect(url_for("customer.list_customers"))


@customer_bp.route("/customers/<int:cid>/documents/<int:doc_id>")
@login_required
def download_document(cid, doc_id):
    c = Customer.query.get_or_404(cid); _own(c)
    doc = CustomerDocument.query.get_or_404(doc_id)
    if doc.customer_id != c.id or doc.user_id != current_user.id:
        abort(403)
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], f"customer_{cid}")
    return send_from_directory(
        folder, doc.stored_name,
        as_attachment=False,
        download_name=doc.original_name,
        mimetype=doc.mime_type or "application/octet-stream",
    )


@customer_bp.route("/customers/<int:cid>/documents/<int:doc_id>/delete", methods=["POST"])
@login_required
def delete_document(cid, doc_id):
    c = Customer.query.get_or_404(cid); _own(c)
    doc = CustomerDocument.query.get_or_404(doc_id)
    if doc.customer_id != c.id or doc.user_id != current_user.id:
        abort(403)
    try:
        path = os.path.join(
            current_app.config["UPLOAD_FOLDER"], f"customer_{cid}", doc.stored_name
        )
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
    db.session.delete(doc); db.session.commit()
    flash("Document deleted.", "info")
    return redirect(url_for("customer.view", cid=cid))


@customer_bp.route("/customers/<int:cid>/documents/<int:doc_id>/edit")
@login_required
def edit_document(cid, doc_id):
    """Image editor: crop/rotate/filter + one-click Replica (copy) and PDF export.
    Works client-side using HTML canvas + jsPDF (no server processing needed)."""
    c = Customer.query.get_or_404(cid); _own(c)
    doc = CustomerDocument.query.get_or_404(doc_id)
    if doc.customer_id != c.id or doc.user_id != current_user.id:
        abort(403)
    return render_template("customer/edit_document.html", c=c, doc=doc)
