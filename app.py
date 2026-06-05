import os
from flask import Flask, render_template
from flask_login import current_user
from sqlalchemy import inspect, text
from whitenoise import WhiteNoise

from config import Config
from extensions import db, login_manager, migrate, csrf, limiter
from models import User

from routes.public import public_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.customer import customer_bp
from routes.service import service_bp
from routes.admin import admin_bp
from routes.handoff import handoff_bp
from routes.payment import payment_bp
from routes.premium import premium_bp
from routes.export import export_bp


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)

    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(int(uid))

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(service_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(premium_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(handoff_bp)

    @app.errorhandler(404)
    def nf(e):
        return render_template("errors/not_found.html"), 404

    @app.errorhandler(403)
    def fb(e):
        # Never shut the user out — show a friendly popup and let them
        # continue using the app.
        return render_template("errors/unauthorized.html"), 403

    @app.errorhandler(500)
    def ie(e):
        return render_template("errors/unauthorized.html",
                               title="Something went wrong",
                               desc="An unexpected error occurred, but the app is still running. Please try again."), 500

    with app.app_context():
        try:
            db.create_all()
            sync_schema()
            seed_admin(app)
        except Exception as e:
            print(f"[startup] Database init failed: {e}")
            raise

    # Serve static files in production via WhiteNoise
    app.wsgi_app = WhiteNoise(app.wsgi_app, root=os.path.join(os.path.dirname(__file__), "static"), prefix="static/")
    return app


def _sa_type_to_sql(col, dialect_name):
    try:
        return col.type.compile(dialect=db.engine.dialect)
    except Exception:
        return str(col.type)


def sync_schema():
    """Add any columns defined in models but missing in the live DB.

    This handles cases where an existing database was created with an
    older version of the schema (e.g. before `users.full_name` existed).
    Only additive changes are performed; no data is dropped.
    """
    try:
        inspector = inspect(db.engine)
        existing_tables = set(inspector.get_table_names())
        for table in db.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue
            existing_cols = {c["name"] for c in inspector.get_columns(table.name)}
            for col in table.columns:
                if col.name in existing_cols:
                    continue
                col_type = _sa_type_to_sql(col, db.engine.dialect.name)
                nullable = "" if col.nullable else " NOT NULL"
                default_clause = ""
                if col.server_default is not None:
                    default_clause = f" DEFAULT {col.server_default.arg}"
                elif col.default is not None and getattr(col.default, "is_scalar", False):
                    val = col.default.arg
                    if isinstance(val, bool):
                        default_clause = f" DEFAULT {'TRUE' if val else 'FALSE'}"
                    elif isinstance(val, (int, float)):
                        default_clause = f" DEFAULT {val}"
                    elif isinstance(val, str):
                        default_clause = f" DEFAULT '{val}'"
                # If NOT NULL with no default, relax to NULL to avoid failures on existing rows
                if not col.nullable and not default_clause:
                    nullable = ""
                ddl = f'ALTER TABLE "{table.name}" ADD COLUMN IF NOT EXISTS "{col.name}" {col_type}{default_clause}{nullable}'
                with db.engine.begin() as conn:
                    try:
                        conn.execute(text(ddl))
                    except Exception as e:
                        # Fallback without IF NOT EXISTS for non-PG dialects
                        try:
                            conn.execute(text(
                                f'ALTER TABLE "{table.name}" ADD COLUMN "{col.name}" {col_type}{default_clause}{nullable}'
                            ))
                        except Exception as e2:
                            print(f"[sync_schema] Skipped {table.name}.{col.name}: {e2}")
    except Exception as e:
        print(f"[sync_schema] Failed: {e}")


def _relax_legacy_columns():
    """Drop NOT NULL on any DB column that is not declared in the current
    SQLAlchemy model (e.g. `username`, `is_verified` from older schemas)
    so inserts driven by the current model don't fail."""
    try:
        insp = inspect(db.engine)
        for table in db.metadata.sorted_tables:
            if not insp.has_table(table.name):
                continue
            model_cols = {c.name for c in table.columns}
            for db_col in insp.get_columns(table.name):
                name = db_col["name"]
                if name in model_cols:
                    continue
                if db_col.get("nullable", True):
                    continue
                try:
                    with db.engine.begin() as conn:
                        conn.execute(text(
                            f'ALTER TABLE "{table.name}" ALTER COLUMN "{name}" DROP NOT NULL'
                        ))
                        print(f"[relax_legacy] dropped NOT NULL on {table.name}.{name}")
                except Exception as e:
                    print(f"[relax_legacy] {table.name}.{name}: {e}")
    except Exception as e:
        print(f"[relax_legacy] Failed: {e}")


def seed_admin(app):
    _relax_legacy_columns()
    email = (app.config.get("ADMIN_EMAIL") or "").strip().lower()
    password = (app.config.get("ADMIN_PASSWORD") or "").strip()
    if not email or not password:
        print("[seed_admin] ADMIN_EMAIL / ADMIN_PASSWORD not configured; skipping.")
        return
    from routes.admin import _sync_env_admin
    existed = User.query.filter_by(email=email).first() is not None
    _sync_env_admin(email, password)
    if existed:
        print(f"[seed_admin] Super admin ready and synced from env: {email}")
    else:
        print(f"[seed_admin] Created super admin from env: {email}")


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
