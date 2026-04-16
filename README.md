# GA Training Portal (FastAPI + PostgreSQL)

Production-ready role-based Student Conduct training portal with editable content, secure login, and Railway deployment support.

## Features
- FastAPI server-rendered portal (Jinja2).
- Roles: **admin** (edit + view) and **user** (view-only).
- Session-based auth with server-side role checks.
- Bcrypt password hashing via Passlib (`bcrypt_sha256` with bcrypt backend for better long-password safety).
- CSRF token validation on login/logout/admin update forms.
- SQLAlchemy ORM models: `User`, `Role`, `EditableContent`.
- Alembic migration included.
- Seed logic for initial roles/users/default content.
- Railway-ready config with `DATABASE_URL` and `Procfile`.

## Project Structure
- `app/main.py` - app startup, middleware, routers.
- `app/routes/auth.py` - `/login`, `/logout`.
- `app/routes/portal.py` - protected content pages.
- `app/routes/admin.py` - admin-only editor routes.
- `app/models.py` - SQLAlchemy models.
- `app/seed.py` - idempotent seed function.
- `scripts/seed.py` - executable seed script.
- `alembic/versions/20260408_01_init.py` - sample migration.

## Environment Variables
Create `.env` locally:

```env
SECRET_KEY=replace-with-long-random-secret
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ga_training
SECURE_COOKIES=false
NOVA_API_KEY=replace-with-your-nova-developer-key
NOVA_BASE_URL=https://api.nova.amazon.com/v1
NOVA_MODEL=amazon.nova-lite-v1:0
HANDBOOK_PATH=app/data/student_handbook.txt
TRAINING_CONTENT_PATH=app/templates
```

> On Railway, use Railway Variables UI to set `SECRET_KEY` and let Railway PostgreSQL provide `DATABASE_URL`.

## Local Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run migration:
   ```bash
   alembic upgrade head
   ```
3. Seed users/content:
   ```bash
   python scripts/seed.py
   ```
4. Start app:
   ```bash
   uvicorn app.main:app --reload
   ```
5. Open `http://127.0.0.1:8000`.

## AI Chat Grounding Notes
- The AI chat page is available at `/ai-chat`.
- Backend endpoint is `/api/ai-chat` (authenticated session required).
- Chat authentication is API key based and uses `Authorization: Bearer <NOVA_API_KEY>`.
- Knowledge grounding loads:
  - training page HTML from `TRAINING_CONTENT_PATH` (defaults to `app/templates`)
  - handbook text from `HANDBOOK_PATH` (supports `.txt`, `.md`, `.pdf` with `pypdf`)
- Responses include source labels such as `Training: Hearing` and `Student Handbook`.
- The assistant is informational only and does not make official conduct decisions.

## Seeded Users
- Admin username: `DAVE`
- User username: `Stconduct`

Passwords are stored hashed only; credentials are seeded server-side, never in frontend code.

## Railway Deployment
1. Push this repo to GitHub.
2. In Railway: **New Project → Deploy from GitHub Repo**.
3. Add a PostgreSQL service in the same Railway project.
4. Ensure variables:
   - `DATABASE_URL` (from Railway PostgreSQL)
   - `SECRET_KEY` (set manually)
   - `SECURE_COOKIES=true`
5. Railway will install from `requirements.txt`.
6. Start command (or Procfile):
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
7. Run migration/seed (Railway shell or release step):
   ```bash
   alembic upgrade head && python scripts/seed.py
   ```

## Example: DB-backed render + admin edit
- DB-backed page render example: `app/routes/portal.py` uses `get_page_content()` then renders `app/templates/page.html`.
- Admin edit form example: `app/templates/admin_page_edit.html` posts to `app/routes/admin.py` route `/admin/content/{page_name}/{section_key}`.
