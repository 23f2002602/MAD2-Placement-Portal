# PlaceMe — Placement Portal

A college placement portal with Flask backend and Vue.js frontend.

## Folder Structure

```
MAD2/
├── backend/          ← Flask REST API (Python)
│   ├── app/
│   │   ├── __init__.py         # App factory
│   │   ├── config.py           # Settings (reads from .env)
│   │   ├── extensions.py       # DB, JWT, Cache, Mail
│   │   ├── models.py           # Database tables
│   │   ├── celery_worker.py    # Background task setup
│   │   ├── api/
│   │   │   ├── auth.py         # Login, Register
│   │   │   ├── admin.py        # Admin actions
│   │   │   ├── company.py      # Company actions
│   │   │   ├── student.py      # Student actions
│   │   │   ├── drives.py       # Public drive listing
│   │   │   └── decorators.py   # @role_required decorator
│   │   └── tasks/
│   │       ├── reminders.py    # Daily email reminders
│   │       ├── monthly_report.py # Monthly admin report
│   │       └── export_csv.py   # Async CSV export
│   ├── run.py            # Start Flask server
│   ├── requirements.txt  # Python packages
│   └── .env              # Environment variables (don't commit!)
│
└── frontend/         ← Vue 3 + Vite SPA
    ├── src/
    │   ├── main.js             # App entry point
    │   ├── App.vue             # Root component
    │   ├── api.js              # All API calls (axios)
    │   ├── store.js            # Global state (reactive)
    │   ├── router/index.js     # Vue Router + guards
    │   └── views/
    │       ├── LoginView.vue        # Login page
    │       ├── RegisterView.vue     # Registration
    │       ├── AdminDashboard.vue   # Admin panel
    │       ├── CompanyDashboard.vue # Company panel
    │       ├── StudentDashboard.vue # Student panel
    │       └── EditProfile.vue      # Profile editor
    ├── index.html        # HTML shell
    ├── vite.config.js    # Vite + proxy config
    └── package.json      # Node packages
```

## How to Run

### Step 1 — Start the Backend (Flask)

```bash
cd backend
python run.py
```
Flask will start at: http://localhost:5000

### Step 2 — Start the Frontend (Vue)

Open a new terminal:
```bash
cd frontend
npm run dev
```
Open your browser at: **http://localhost:5173**

> Vite proxies all `/api/*` requests to Flask automatically.

---

## Default Admin Login

```
Email:    admin@placement.com
Password: Admin@123
```
Admin is created automatically on first backend run.

---

## Optional: Celery (Background Jobs)

Requires Redis running first.

```bash
# Worker (processes tasks)
cd backend
celery -A app.celery_worker.celery_app worker --loglevel=info

# Beat scheduler (triggers scheduled jobs)
celery -A app.celery_worker.celery_app beat --loglevel=info
```

## Email Setup

Edit `backend/.env`:
```
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_DEFAULT_SENDER=your-gmail@gmail.com
```
Generate a Gmail App Password at: myaccount.google.com/apppasswords
