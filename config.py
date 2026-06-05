import os
from urllib.parse import urlparse, urlunparse
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _normalize_db_url(url: str) -> str:
    if not url:
        return url
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    # Render internal hostnames (e.g. dpg-xxxxx-a) don't resolve from
    # services in another region. If we detect one, append the external
    # suffix so DNS works from anywhere.
    try:
        parts = urlparse(url)
        host = parts.hostname or ""
        if host.startswith("dpg-") and "." not in host:
            region = os.environ.get("RENDER_DB_REGION", "oregon")
            new_host = f"{host}.{region}-postgres.render.com"
            userinfo = ""
            if parts.username:
                userinfo = parts.username
                if parts.password:
                    userinfo += f":{parts.password}"
                userinfo += "@"
            port = f":{parts.port}" if parts.port else ""
            netloc = f"{userinfo}{new_host}{port}"
            url = urlunparse(parts._replace(netloc=netloc))
    except Exception:
        pass
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    DATABASE_URL = _normalize_db_url(os.environ.get("DATABASE_URL", "postgresql://arcade_hub_db_005a_user:1eFI2CcvxvhXrdzMiTh8y9Ap2l8jdhIo@dpg-d876pqt7vvec738o5r10-a/arcade_hub_db_005a"))
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or f"sqlite:///{os.path.join(BASE_DIR, 'cybercafe.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    WTF_CSRF_TIME_LIMIT = None
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 30
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@cybercafe.local")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@12345")
    ADMIN_UPI_ID = os.environ.get("ADMIN_UPI_ID", "admin@upi")
    ADMIN_UPI_NAME = os.environ.get("ADMIN_UPI_NAME", "CyberCafe ERP")
