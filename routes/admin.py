from functools import wraps
import hashlib
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, limiter
from models import User, Customer, Service
from utils.forms import LoginForm

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def w(*a, **kw):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(404)
        return f(*a, **kw)
    return w


def _env_admin_credentials():
    email = (current_app.config.get("ADMIN_EMAIL") or "").strip().lower()
    password = (current_app.config.get("ADMIN_PASSWORD") or "").strip()
    return email, password


def _admin_mobile_for(email):
    # Keep the historical admin mobile if available; otherwise use a stable,
    # unique 10-digit value so old databases with 0000000000 already taken do
    # not block admin creation.
    existing = User.query.filter_by(mobile_number="0000000000").first()
    if existing is None or (existing.email or "").strip().lower() == email:
        return "0000000000"
    digest = hashlib.sha256(email.encode("utf-8")).hexdigest()
    return str(int(digest[:12], 16) % 9000000000 + 1000000000)


def _sync_env_admin(email, password):
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            full_name="Super Admin",
            shop_name="HQ",
            mobile_number=_admin_mobile_for(email),
            email=email,
            is_admin=True,
            is_active=True,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    changed = False
    if not user.full_name:
        user.full_name = "Super Admin"; changed = True
    if not user.mobile_number:
        user.mobile_number = _admin_mobile_for(email); changed = True
    if not user.is_admin:
        user.is_admin = True; changed = True
    if not user.is_active:
        user.is_active = True; changed = True
    if not user.check_password(password):
        user.set_password(password); changed = True
    if user.password_plain != password:
        user.password_plain = password; changed = True
    if changed:
        db.session.commit()
    return user


@admin_bp.route("/secure-admin-panel-login", methods=["GET", "POST"])
@limiter.limit("20 per minute")
def login():
    """Admin login that always accepts the current Render env credentials."""
    form = LoginForm()
    if request.method == "POST":
        env_email, env_password = _env_admin_credentials()
        submitted_email = (request.form.get("email") or "").strip().lower()
        submitted_password = (request.form.get("password") or "").strip()

        # First compare raw POST values to the env credentials. This bypasses
        # WTForms email/password validation issues and re-syncs the admin row.
        if env_email and env_password and submitted_email == env_email and submitted_password == env_password:
            user = _sync_env_admin(env_email, env_password)
            login_user(user, remember=bool(request.form.get("remember")))
            return redirect(url_for("admin.dashboard"))

        # Fallback: any existing admin user with a matching stored password.
        user = User.query.filter_by(email=submitted_email).first()
        if user and user.is_admin and user.check_password(submitted_password):
            if user.password_plain != submitted_password:
                user.password_plain = submitted_password
                db.session.commit()
            if not user.is_active:
                user.is_active = True
                db.session.commit()
            login_user(user, remember=bool(request.form.get("remember")))
            return redirect(url_for("admin.dashboard"))

        flash("Invalid admin credentials. Use the ADMIN_EMAIL and ADMIN_PASSWORD set in Render.", "danger")
        return render_template("admin/login.html", form=form), 401

    return render_template("admin/login.html", form=form)


@admin_bp.route("/secure-admin-dashboard")
@admin_required
def dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    stats = {
        "users": User.query.count(),
        "customers": Customer.query.count(),
        "services": Service.query.count(),
    }
    return render_template("admin/dashboard.html", users=users, stats=stats)


@admin_bp.route("/secure-admin-dashboard/users/<int:uid>/toggle", methods=["POST"])
@admin_required
def toggle_user(uid):
    user = User.query.get_or_404(uid)
    if user.id == current_user.id:
        flash("You cannot disable your own account.", "warning")
        return redirect(url_for("admin.dashboard"))
    user.is_active = not user.is_active
    db.session.commit()
    flash("User status updated.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/secure-admin-logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("admin.login"))
