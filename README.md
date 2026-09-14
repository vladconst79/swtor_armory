# SWTOR Armory

SWTOR Armory is a standalone remake of the original Odoo 16 `swtor_armory` addon. It keeps the same goal, helping Star Wars: The Old Republic players manage character and legacy information, while moving the project onto a more modern and independent application stack.

The old Odoo addon was published separately at
[vladconst79/swtor_armory_odoo](https://github.com/vladconst79/swtor_armory_odoo).

This repository is the new implementation:

```text
backend/   FastAPI + SQLAlchemy + Alembic + PostgreSQL
frontend/  React + TypeScript + React Admin
```

The Odoo addon remains the historical reference for the initial data model, permissions, and domain behavior.

## Features

* Manage SWTOR characters, guilds, roles, origin stories, combat styles, titles, vehicles, and notes.
* Track loadouts, items, crew skills, operation bosses, weekly lockouts, and related gameplay metadata.
* Provide a REST API backed by PostgreSQL with Alembic-managed migrations.
* Enforce owner-only access for player-owned records and admin-only writes for shared reference data.
* Expose an admin frontend built with React Admin for practical data entry and maintenance.
* Seed SWTOR reference data idempotently after database migrations.

## Project Layout

```text
.
├── backend/        FastAPI backend
├── frontend/       Vite React frontend
├── ToDO.md         implementation roadmap
├── .gitlab-ci.yml  GitLab CI test and build pipeline
└── README.md
```

## Requirements

* Python 3.11+
* Node.js 26+ and npm
* PostgreSQL

## Backend Setup

Create a virtual environment and install the backend dependencies:

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

Run backend checks used by CI:

```bash
cd backend
source .venv/bin/activate
python -m compileall app alembic tests
python -m alembic heads
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

Create or update `backend/.env` so `DATABASE_URL` points at the target database, then run migrations:

```bash
cd backend
.venv/bin/python -m alembic upgrade head
```

Seed the reference data after migrations:

```bash
cd backend
.venv/bin/python -c "from app.db.session import SessionLocal; from app.db.seed import seed_reference_data; db = SessionLocal(); seed_reference_data(db); db.close()"
```

The seed script is idempotent and can be run again without duplicating reference records. The API does not currently auto-seed on startup, so deployments should run migrations and reference seeding as explicit deploy steps.

## Security Model

The old Odoo module used owner-only record rules based on `create_uid = user.id` for user-owned data. In this rebuild, that behavior must be enforced in the FastAPI backend.

Normal users should only manage their own:

* characters
* loadouts
* items
* character crew skill relations
* operation lockouts

SWTOR admins should be able to manage reference data and all user-owned records.

## CI

GitLab CI runs backend tests, frontend linting, and a frontend production build. The pipeline is defined in `.gitlab-ci.yml`.

## Relationship to the Odoo Project

This project is intentionally not an Odoo module. It is a remake of `swtor_armory` using standalone services and frontend tooling so it can evolve independently of an Odoo deployment.

The Odoo repository remains useful as the historical implementation and migration reference. This project should preserve the important behavior from that addon while expressing it through explicit database migrations, API tests, and frontend resources.

## Implementation Plan

See `ToDO.md` for the staged rebuild checklist.

## Community Intent

SWTOR Armory is a fan-made utility project. It is not affiliated with, endorsed by, sponsored by, or approved by Electronic Arts, BioWare, Lucasfilm, or Disney. Star Wars, Star Wars: The Old Republic, SWTOR, and related names and assets belong to their respective owners.

The project exists to help players organize their gameplay information and to give the community a practical base to improve together.

## License

This project is licensed under the GNU Affero General Public License v3.0 or later. See [LICENSE](LICENSE) for the full license text.
