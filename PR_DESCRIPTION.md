Title: Prepare Render deployment — SQLAlchemy, Alembic, Redis rate limiting, SEO & accessibility

Summary

This PR prepares the project for production deployment on Render:

- Migrate SQLite raw usage to SQLAlchemy ORM and `DATABASE_URL` support
- Add Alembic migration scaffolding and initial migration (contact_messages table)
- Add Redis-backed rate limiting using `slowapi` (falls back to memory if `REDIS_URL` not set)
- Add honeypot field and frontend integration to reduce spam
- Accessibility/SEO improvements: OG tags, robots.txt, avoid hiding system cursor
- CI workflow to run basic import/health checks
- `render.yaml` updated with `DATABASE_URL` and `REDIS_URL` placeholders

How to test locally

1. Install deps:

```bash
python -m pip install -r backend/requirements.txt
```

2. Run backend:

```bash
uvicorn backend.main:app --reload --port 8000
curl http://127.0.0.1:8000/api/health
```

3. Run migrations (optional, uses sqlite locally):

```bash
cd backend
export DATABASE_URL=sqlite:///./portfolio.db
alembic upgrade head
```

Deployment notes

- Provision a managed Postgres and set `DATABASE_URL` on the backend service.
- Provision Redis and set `REDIS_URL` for distributed rate limiting.
- Populate SMTP envs for email notifications.
- After setting `DATABASE_URL`, run `alembic upgrade head` on the deployment host.

Security

- `ADMIN_API_KEY` protects `/api/messages` — keep secret and rotate via Render UI if needed.

Files changed

- `backend/main.py`, `backend/requirements.txt`, `backend/alembic/*`, `render.yaml`, `Web Dev/index.html`, `Web Dev/script.js`, `Web Dev/style.css`, `Web Dev/robots.txt`, `.github/workflows/ci.yml`, `README.md`

Notes

- `psycopg2-binary` is commented out in `requirements.txt` for local convenience; enable in production build environment or install a compatible wheel there.
- The rate limiter uses `REDIS_URL` when available; fallback memory limiter is used otherwise.

Please review and merge when ready.