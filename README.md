# SWTOR Armory

SWTOR Armory is a rebuild of the old Odoo 16 `swtor_armory` addon as a standalone web app.

The target stack is:

```text
backend/   FastAPI + SQLAlchemy + Alembic + PostgreSQL
frontend/  React + TypeScript + React Admin
```

The old Odoo addon is the source of truth for the initial rebuild:

```text
/opt/odoo16c/custom/addons/swtor_armory/docs/rebuild-notes.md
/opt/odoo16c/custom/addons/swtor_armory/models/
/opt/odoo16c/custom/addons/swtor_armory/security/
/opt/odoo16c/custom/addons/swtor_armory/views/menu.xml
/opt/odoo16c/custom/addons/swtor_armory/__init__.py
```

## Project Layout

```text
.
├── backend/    FastAPI backend
├── frontend/   Vite React frontend
├── ToDO.md     implementation roadmap
└── README.md
```

## Requirements

* Python 3.11+
* Node.js and npm
* PostgreSQL

## Backend Setup

The virtualenv already lives at `backend/.venv`.

When setting up from scratch:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

Run backend tests:

```bash
cd backend
source .venv/bin/activate
pytest
```

## Frontend Setup

Install dependencies:

```bash
cd frontend
npm install
```

Run the frontend dev server:

```bash
cd frontend
npm run dev
```

Build the frontend:

```bash
cd frontend
npm run build
```

Run linting:

```bash
cd frontend
npm run lint
```

Preview the production build:

```bash
cd frontend
npm run preview
```

## Database

The target database is PostgreSQL. Migrations live under `backend/alembic/` and are managed with Alembic.

Expected local environment variables are documented in `backend/.env.example`.

## Security Model

The old Odoo module used owner-only record rules based on `create_uid = user.id` for user-owned data. In this rebuild, that behavior must be enforced in the FastAPI backend.

Normal users should only manage their own:

* characters
* loadouts
* items
* character crew skill relations
* operation lockouts

SWTOR admins should be able to manage reference data and all user-owned records.

## Implementation Plan

See `ToDO.md` for the staged rebuild checklist.
