# Software Version Management System

A centralized internal web application for tracking all software systems and their versions.

## Features

- **System Management** - Track all software systems with metadata
- **Version Control** - Create, edit, release, and archive versions
- **Current Version** - Prominently displays the current version of every system
- **Version History** - Complete timeline of all versions per system
- **Version Comparison** - Compare changes between two versions
- **Change Tracking** - Track individual changes (features, fixes, improvements)
- **Search** - Global search across systems and versions
- **Reports** - Current versions, version history, releases, and changes reports
- **Audit Logs** - Track all important actions
- **User Management** - Role-based access (Admin / User)

## Architecture

- **Backend**: Python 3.12+, Flask, SQLAlchemy, Flask-Login
- **Frontend**: HTML5, CSS3, Bootstrap 5, Jinja2
- **Database**: SQLite (development), PostgreSQL (production)
- **Pattern**: Application Factory, Blueprints, Service Layer

## Installation

### 1. Clone and navigate

```bash
cd versions
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment

```bash
copy .env.example .env
```

Edit `.env` and set `SECRET_KEY` and `DATABASE_URL`.

### 5. Initialize database and seed data

```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

python seed.py
```

### 6. Run the application

```bash
python run.py
```

Open http://localhost:5000

## Demo Credentials

| Username | Password   | Role  |
|----------|------------|-------|
| admin    | admin123   | Admin |
| ahmed    | user123    | User  |
| mohamed  | user123    | User  |
| sara     | user123    | User  |

## Testing

```bash
pytest tests/ -v
```

## Project Structure

```
versions/
├── app/
│   ├── __init__.py           # Application factory
│   ├── config.py             # Configuration classes
│   ├── models/               # SQLAlchemy models
│   │   ├── user.py
│   │   ├── system.py
│   │   ├── version.py
│   │   ├── version_change.py
│   │   ├── attachment.py
│   │   └── audit_log.py
│   ├── routes/               # Blueprint routes
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── systems.py
│   │   ├── versions.py
│   │   ├── reports.py
│   │   ├── users.py
│   │   └── audit.py
│   ├── services/             # Business logic
│   │   ├── version_service.py
│   │   ├── audit_service.py
│   │   └── report_service.py
│   ├── templates/            # Jinja2 templates
│   │   ├── base.html
│   │   ├── auth/login.html
│   │   ├── dashboard/index.html
│   │   ├── systems/
│   │   ├── versions/
│   │   ├── reports/
│   │   ├── users/
│   │   └── audit/
│   └── static/               # CSS and JavaScript
│       ├── css/style.css
│       └── js/app.js
├── tests/
│   └── test_app.py
├── migrations/
├── seed.py
├── run.py
├── requirements.txt
├── .env.example
└── README.md
```

## Database Schema

```
User (id, username, email, password_hash, full_name, role, is_active)
  │
System (id, name, code, system_type, description, owner, department, status)
  │
  └── Version (id, system_id, version_number, major, minor, patch, status, release_date)
        │
        └── VersionChange (id, version_id, change_type, title, description)
        │
        └── Attachment (id, version_id, file_name, file_path)

AuditLog (id, user_id, action, entity_type, entity_id, description, created_at)
```

## Version Status Rules

- **Draft**: Being prepared, can be edited
- **Released**: Official version, one per system is "current"
- **Archived**: Historical reference only

When a version is Released, it automatically becomes the current version for that system. The previous current version remains in history but loses the "current" designation.
