from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, limiter
from models import User, Subscription
from utils.forms import RegisterForm, LoginForm

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter((User.email == form.email.data) | (User.mobile_number == form.mobile_number.data)).first():
            flash("Email or mobile already registered.", "danger")
            return render_template("auth/register.html", form=form)
        user = User(
            full_name=form.full_name.data,
            shop_name=form.shop_name.data,
            mobile_number=form.mobile_number.data,
            email=form.email.data.lower(),
            district=form.district.data,
            address=form.address.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()
        db.session.add(Subscription(user_id=user.id))
        db.session.commit()
        flash("Account created. Please login.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("20 per minute")
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("dashboard.index"))
    form = LoginForm()
    if request.method == "POST":
        submitted_email = (request.form.get("email") or "").strip().lower()
        submitted_password = (request.form.get("password") or "").strip()

        # Allow admin to sign in from the regular /login page using env creds.
        # Do this before WTForms validation so env admin login cannot be blocked
        # by browser/form validation edge cases.
        env_email = (current_app.config.get("ADMIN_EMAIL") or "").strip().lower()
        env_password = (current_app.config.get("ADMIN_PASSWORD") or "").strip()
        if env_email and env_password and submitted_email == env_email and submitted_password == env_password:
            from routes.admin import _sync_env_admin
            user = _sync_env_admin(env_email, env_password)
            if not user.password_plain:
                user.password_plain = submitted_password
                from extensions import db as _db; _db.session.commit()
            login_user(user, remember=bool(request.form.get("remember")))
            return redirect(url_for("admin.dashboard"))

        if form.validate_on_submit():
            user = User.query.filter_by(email=submitted_email).first()
            if user and user.check_password(submitted_password) and user.is_active:
                if user.password_plain != submitted_password:
                    user.password_plain = submitted_password
                    db.session.commit()
                login_user(user, remember=form.remember.data)
                if user.is_admin:
                    return redirect(url_for("admin.dashboard"))
                return redirect(request.args.get("next") or url_for("dashboard.index"))
        flash("Invalid credentials.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("public.home"))
