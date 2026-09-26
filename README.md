# Event Management System (EMS)

EMS is a Flask web application for managing events, attendee registrations, and event operations. It also includes an admin-only patient and medical-record module.

## Features

- User registration, login, profile management, and personal dashboard.
- Event browsing and search, event registration, QR-code tickets, and ticket downloads.
- Capacity-aware event waitlists with automatic promotion when a seat becomes available.
- Admin event and user management, registration lists, and event statistics.
- QR check-in, attendance reports, event analytics, calendar (`.ics`) downloads, and attendee feedback.
- Admin patient records with patient search, status filters, and medical-record management.
- Optional email and SMS notifications (SMTP and Twilio); notification outcomes are logged.
- Responsive Bootstrap interface with a persistent light/dark theme preference.

## Technology

- Python and Flask 3.1
- Flask-SQLAlchemy / SQLAlchemy with SQLite for development and MySQL configuration for production
- Flask-Login and Flask-Bcrypt
- Jinja templates, Bootstrap 5, JavaScript, and Bootstrap Icons
- `qrcode` and Pillow for QR tickets and image handling

## Project Layout

```text
app/
  __init__.py              Flask application factory and extension setup
  models.py                Core database models
  feature_models.py        Waitlist, attendance, feedback, notification models
  services.py              Email, SMS, and optional S3-compatible uploads
  routes/                  Authentication, user, admin, patient, and feature routes
  templates/               Shared, user, admin, and authentication pages
  static/                  CSS, JavaScript, event uploads, and QR codes
config.py                  Development, production, and testing configurations
run.py                     Development server entry point
seed_data.py               Destructive development sample-data seeder
requirements.txt           Python dependencies
documentation.md           Extended project documentation
```

## Run Locally

You need Python 3.10 or later and pip. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py
```

For macOS or Linux, activate the virtual environment with:

```bash
source .venv/bin/activate
```

Open <http://127.0.0.1:5000>. The default development configuration uses SQLite and creates the database tables when the app starts. The database is stored in the Flask instance directory.

### Optional Sample Data

To create sample users and events, run:

```bash
python seed_data.py
```

**Warning:** the seeder drops and recreates all tables in the development database before inserting sample data. Do not run it against data you need to keep.

Seeded sample user accounts use the password `password123`; for example, `john@example.com`. The seeder also creates an `admin` account, but the current admin login route uses separate hard-coded credentials, so the seeded admin account does not work for admin login. See [Security Notes](#security-notes) before using admin access.

## Main Pages

| Page | Route | Access |
| --- | --- | --- |
| Home | `/` | Public |
| User registration | `/auth/register` | Public |
| User login | `/auth/login` | Public |
| Admin login | `/auth/admin-login` | Public |
| User dashboard and events | `/user/dashboard`, `/user/events` | Signed-in users |
| User tickets and profile | `/user/my-tickets`, `/user/profile` | Signed-in users |
| Admin dashboard and event management | `/admin/dashboard`, `/admin/events` | Admin |
| Admin analytics and QR check-in | `/admin/features/analytics`, `/admin/features/checkin` | Admin |
| Patient records | `/admin/patients/` | Admin |

## Configuration

`run.py` loads a `.env` file when present. Development uses SQLite by default. To configure an environment, copy `.env.example` to `.env` and set values appropriate for your setup. Do not commit real secrets.

For the MySQL configuration, set `FLASK_ENV=production`, `DATABASE_URL` (for example, `mysql+pymysql://user:password@host/database`), and a strong `SECRET_KEY`. SMTP, Twilio, and S3-compatible storage settings are optional and are only used when configured.

## Security Notes

- The current admin login credentials are hard-coded in `app/routes/auth.py`; the `ADMIN_EMAIL` and `ADMIN_PASSWORD` entries in `.env.example` are not currently read by that route. Replace this implementation with environment-backed credentials before exposing admin access.
- `run.py` is a development entry point and enables Flask debug mode when run directly. Do not use it as a production server; deploy behind a production WSGI server after reviewing the configuration.
- Change the development secret key and use a strong secret key for any deployment.
- Sample account passwords are for local development only.

## Documentation

See [documentation.md](documentation.md), [setup_guide.md](setup_guide.md), and [SECURITY_BEST_PRACTICES.md](SECURITY_BEST_PRACTICES.md) for additional project details.