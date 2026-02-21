# Portfolio Backend (FastAPI)

## 1) Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 2) Run API

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## 3) Endpoints

- `GET /api/health`
- `POST /api/contact`
- `GET /api/messages` (protected, requires `x-api-key` header)

### Sample `POST /api/contact` body

```json
{
  "name": "Sam Sparxz",
  "email": "mr.samsparxz@gmail.com",
  "subject": "Internship Opportunity",
  "message": "Hi Sam, I would like to discuss a collaboration."
}
```

### Sample protected `GET /api/messages`

```bash
curl -H "x-api-key: replace-with-strong-key" "http://127.0.0.1:8000/api/messages?limit=20"
```

## Email Notifications

Set these in `.env` to get an email whenever a message is submitted:

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USE_TLS`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_FROM`
- `NOTIFY_TO`

## Notes

- Messages are stored in `backend/portfolio.db` (SQLite).
- Update `ALLOWED_ORIGINS` in `.env` if your frontend runs on a different port/domain.
