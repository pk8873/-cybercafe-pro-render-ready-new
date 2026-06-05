import os
import json
from functools import lru_cache
from flask import Blueprint, render_template, send_from_directory, current_app, request, abort

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    return render_template("public/home.html")


@public_bp.route("/install")
def install():
    return render_template("install.html")


# --- Guides (operator help library) ---
@lru_cache(maxsize=1)
def _load_guides():
    path = os.path.join(current_app.root_path, "guides.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


@public_bp.route("/guides")
def guides_list():
    guides = _load_guides()
    q = (request.args.get("q") or "").strip().lower()
    cat = request.args.get("cat") or "All"
    categories = ["All"] + sorted({g.get("category", "Other") for g in guides})
    items = guides
    if q:
        items = [g for g in items if q in g.get("name", "").lower() or q in g.get("summary", "").lower()]
    if cat and cat != "All":
        items = [g for g in items if g.get("category") == cat]
    return render_template("guides/list.html", guides=items, categories=categories, q=q, cat=cat)


@public_bp.route("/guides/<slug>")
def guide_detail(slug):
    guides = _load_guides()
    g = next((x for x in guides if x.get("slug") == slug), None)
    if not g:
        abort(404)
    related = [x for x in guides if x.get("slug") != slug and x.get("category") == g.get("category")][:3]
    return render_template("guides/detail.html", g=g, related=related)


# --- PWA: serve manifest and service worker from site root so scope = "/" ---
@public_bp.route("/manifest.webmanifest")
def manifest():
    root = os.path.join(current_app.root_path, "static")
    return send_from_directory(root, "manifest.webmanifest", mimetype="application/manifest+json")


@public_bp.route("/sw.js")
def service_worker():
    root = os.path.join(current_app.root_path, "static")
    resp = send_from_directory(root, "sw.js", mimetype="application/javascript")
    resp.headers["Service-Worker-Allowed"] = "/"
    resp.headers["Cache-Control"] = "no-cache"
    return resp
