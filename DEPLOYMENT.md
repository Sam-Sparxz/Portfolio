# Deployment & Environment Notes

This file outlines environment variables and deployment tips for the portfolio backend and frontend.

Backend (FastAPI)

- `DATABASE_URL` — Database DSN. Defaults to a local SQLite database at `backend/portfolio.db` when unset.
- `REDIS_URL` — Optional Redis URL for `slowapi` rate limiting. If unset, in-memory limiter is used.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_USE_TLS` — Configure SMTP to enable email notifications when new contact messages arrive.
- `NOTIFY_TO` — Email address that receives contact notifications.
- `ADMIN_API_KEY` — Required to access the `/api/messages` admin endpoint. Set a strong secret in production.
- `ALLOWED_ORIGINS` — Comma-separated list of allowed CORS origins for the API. If empty, `*` is allowed by default in dev.

Start the backend (development):

```bash
# from project root
/usr/bin/python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend

- The frontend is static files in `Web Dev/`. During deploy, set the `meta[name="api-base-url"]` in `Web Dev/index.html` (or inject at build time) to point to the production API base URL (no trailing slash). Example:

```html
<meta name="api-base-url" content="https://api.yourdomain.com" />
```

Local preview

```bash
# serve the static site from Web Dev
(cd "Web Dev" && /usr/bin/python3 -m http.server 5500)
```

Security & notes

- Ensure `ADMIN_API_KEY` is set in production and never exposed to client-side code.
- Use `REDIS_URL` in production for robust distributed rate-limiting.
- For PostgreSQL or other DBs, set `DATABASE_URL` appropriately and run migrations via Alembic (alembic.ini included).

If you want, I can add a small `Makefile` or `Procfile` for common deploy commands.
