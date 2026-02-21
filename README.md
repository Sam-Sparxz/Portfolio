# Portfolio (Sam Sparxz)

This repository contains a static frontend (`Web Dev`) and a FastAPI backend (`backend`).

Quick local run (backend)

```bash
python -m pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Run Alembic migrations (after setting `DATABASE_URL` env)

```bash
cd backend
export DATABASE_URL=sqlite:///./portfolio.db
alembic upgrade head
```

Render deployment notes

- Frontend service: `sam-portfolio-frontend` (static) — serves files from `Web Dev`.
- Backend service: `sam-portfolio-api` (python) — `startCommand` runs `uvicorn main:app`.
- Set `DATABASE_URL` in Render to a managed Postgres connection string for persistence.
- Optionally provision a Redis instance and set `REDIS_URL` for distributed rate-limiting.
- Fill SMTP env vars (`SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `NOTIFY_TO`) to enable email notifications.
- Retrieve or rotate `ADMIN_API_KEY` from the Render service env to access `/api/messages`.

Admin usage example

```bash
curl -H "x-api-key: $ADMIN_API_KEY" "https://sam-portfolio-api.onrender.com/api/messages?limit=25"
```
