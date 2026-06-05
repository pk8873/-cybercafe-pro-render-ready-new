# CyberCafe ERP

All-in-one ERP for Indian cyber cafes — customer ledger, services, payments and reports.

## ✨ What's new in this version

- **🎨 Brand-new 3D / Glassmorphism UI** — aurora gradient backgrounds, floating orbs,
  depth-shadowed cards, push-style 3D buttons, modern Plus Jakarta Sans typography,
  gradient chart fills.
- **📱 QR Document Handoff** — open any customer and click "Receive Documents (QR)".
  A QR code appears. The customer scans it with their phone camera, taps a file or takes
  a photo, and the document is delivered straight to **your operator device** (auto-download).
  **Nothing is saved to the database or to our servers** — files live in memory only and
  are wiped the moment they reach your browser.
- **🧭 Friendlier forms** — labeled fields, placeholders, validation hints, Cancel + Save
  buttons, and a consistent back link.

## 🚀 One-click deploy on Render

1. Upload this folder to a new GitHub repo (or use Render's "Deploy from ZIP").
2. On Render → **New +** → **Blueprint** → point at the repo. `render.yaml` is included.
3. Add a **Postgres** database in Render and copy its `External Database URL` into the
   `DATABASE_URL` env var on the web service.
4. (Optional) override `ADMIN_EMAIL` / `ADMIN_PASSWORD` env vars.
5. Deploy. The first boot creates tables and seeds the admin user.

## 🔧 Local development

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set SECRET_KEY, optional DATABASE_URL
python app.py          # http://localhost:5000
```

## 🔐 Default admin

- Email:    `admin@cybercafe.local`
- Password: `Admin@12345`

Change these via `ADMIN_EMAIL` / `ADMIN_PASSWORD` env vars before first deploy.

## 🗂️ Tech

Flask 3 · SQLAlchemy · Flask-Login · Flask-WTF · Flask-Limiter · Tailwind (CDN) ·
Chart.js · qrcode · WhiteNoise · Gunicorn.
