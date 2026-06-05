"""
Customer Document Handoff via QR.

The operator opens "Receive Documents" on a customer, which mints a
short-lived token and shows a QR. The customer scans the QR on their
phone and uploads photos / PDFs.

Each uploaded file is BOTH:
  - pushed live to the operator's browser via polling (instant download), and
  - persisted to disk and recorded as a CustomerDocument row so the
    operator can re-open the customer later and still see the documents.
"""
import base64
import io
import os
import secrets
import time
import threading
import mimetypes
import uuid

from flask import (
    Blueprint, render_template, abort, request, jsonify, url_for,
    send_file, current_app,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from extensions import csrf, limiter, db
from models import Customer, CustomerDocument

handoff_bp = Blueprint("handoff", __name__)

# token -> {user_id, customer_id, customer_name, created, queue:[...]}
_SESSIONS: dict[str, dict] = {}
_LOCK = threading.Lock()
_TTL_SECONDS = 60 * 60       # 1 hour
_MAX_BYTES = 12 * 1024 * 1024  # 12 MB per file


def _cleanup():
    now = time.time()
    with _LOCK:
        for tok in list(_SESSIONS.keys()):
            if now - _SESSIONS[tok]["created"] > _TTL_SECONDS:
                _SESSIONS.pop(tok, None)


def _customer_dir(cid: int) -> str:
    base = current_app.config["UPLOAD_FOLDER"]
    path = os.path.join(base, f"customer_{cid}")
    os.makedirs(path, exist_ok=True)
    return path


@handoff_bp.route("/customers/<int:cid>/handoff")
@login_required
def handoff(cid):
    c = Customer.query.get_or_404(cid)
    if c.user_id != current_user.id:
        abort(403)
    _cleanup()
    token = secrets.token_urlsafe(16)
    with _LOCK:
        _SESSIONS[token] = {
            "user_id": current_user.id,
            "customer_id": c.id,
            "customer_name": c.full_name,
            "created": time.time(),
            "queue": [],
        }
    upload_url = url_for("handoff.customer_page", token=token, _external=True)
    qr_url = url_for("handoff.qr_png", token=token)
    return render_template(
        "handoff/receive.html",
        c=c, token=token, upload_url=upload_url, qr_url=qr_url,
    )


@handoff_bp.route("/h/qr/<token>.png")
def qr_png(token):
    with _LOCK:
        if token not in _SESSIONS:
            abort(404)
    target = url_for("handoff.customer_page", token=token, _external=True)
    try:
        import qrcode
        img = qrcode.make(target)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return send_file(buf, mimetype="image/png")
    except Exception:
        return send_file(io.BytesIO(b""), mimetype="image/png")


@handoff_bp.route("/h/<token>")
def customer_page(token):
    with _LOCK:
        sess = _SESSIONS.get(token)
    if not sess:
        return render_template("handoff/expired.html"), 404
    return render_template(
        "handoff/customer.html",
        token=token, customer_name=sess["customer_name"],
    )


@handoff_bp.route("/h/<token>/upload", methods=["POST"])
@csrf.exempt
@limiter.limit("60 per hour")
def customer_upload(token):
    with _LOCK:
        sess = _SESSIONS.get(token)
    if not sess:
        return jsonify({"ok": False, "error": "Session expired"}), 404

    files = request.files.getlist("files")
    if not files:
        return jsonify({"ok": False, "error": "No files"}), 400

    cid = sess["customer_id"]
    uid = sess["user_id"]
    folder = _customer_dir(cid)

    accepted = 0
    for f in files:
        if not f or not f.filename:
            continue
        data = f.read(_MAX_BYTES + 1)
        if len(data) > _MAX_BYTES:
            return jsonify({"ok": False, "error": "File too large (max 12MB)"}), 413
        mime = (
            f.mimetype
            or mimetypes.guess_type(f.filename)[0]
            or "application/octet-stream"
        )
        original = secure_filename(f.filename) or "document"
        ext = os.path.splitext(original)[1]
        stored = f"{int(time.time())}_{uuid.uuid4().hex[:10]}{ext}"
        with open(os.path.join(folder, stored), "wb") as out:
            out.write(data)

        try:
            doc = CustomerDocument(
                customer_id=cid,
                user_id=uid,
                original_name=original,
                stored_name=stored,
                mime_type=mime,
                size_bytes=len(data),
            )
            db.session.add(doc)
            db.session.commit()
        except Exception:
            db.session.rollback()

        with _LOCK:
            if token not in _SESSIONS:
                return jsonify({"ok": False, "error": "Session expired"}), 404
            _SESSIONS[token]["queue"].append({
                "name": original,
                "mime": mime,
                "data_b64": base64.b64encode(data).decode("ascii"),
                "size": len(data),
            })
        accepted += 1

    return jsonify({"ok": True, "received": accepted})


@handoff_bp.route("/customers/<int:cid>/handoff/<token>/poll")
@login_required
def operator_poll(cid, token):
    with _LOCK:
        sess = _SESSIONS.get(token)
        if not sess or sess["user_id"] != current_user.id or sess["customer_id"] != cid:
            return jsonify({"ok": False, "expired": True}), 404
        queue = sess["queue"]
        sess["queue"] = []
        sess["created"] = time.time()
    return jsonify({"ok": True, "files": queue})


@handoff_bp.route("/customers/<int:cid>/handoff/<token>/end", methods=["POST"])
@login_required
def end_session(cid, token):
    with _LOCK:
        sess = _SESSIONS.get(token)
        if sess and sess["user_id"] == current_user.id:
            _SESSIONS.pop(token, None)
    return jsonify({"ok": True})
