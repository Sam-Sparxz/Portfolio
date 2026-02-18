from __future__ import annotations

import os
import smtplib
import sqlite3
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "portfolio.db"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


class ContactMessageIn(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    subject: str = Field(min_length=3, max_length=120)
    message: str = Field(min_length=10, max_length=2500)


class ContactMessageOut(BaseModel):
    ok: bool
    message: str


class ContactMessageRecord(BaseModel):
    id: int
    name: str
    email: EmailStr
    subject: str
    message: str
    created_at: str


app = FastAPI(title="Portfolio API", version="1.1.0")

allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [item.strip() for item in allowed_origins_raw.split(",") if item.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def send_email_notification(payload: ContactMessageIn, created_at: str) -> None:
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    notify_to = os.getenv("NOTIFY_TO", "").strip()

    if not smtp_host or not notify_to:
        return

    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_from = os.getenv("SMTP_FROM", smtp_user).strip()

    if not smtp_from:
        return

    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").strip().lower() in {"1", "true", "yes"}

    msg = EmailMessage()
    msg["Subject"] = f"New Portfolio Message: {payload.subject}"
    msg["From"] = smtp_from
    msg["To"] = notify_to
    msg.set_content(
        "\n".join(
            [
                "New contact message received.",
                "",
                f"Name: {payload.name}",
                f"Email: {payload.email}",
                f"Subject: {payload.subject}",
                f"Created (UTC): {created_at}",
                "",
                "Message:",
                payload.message,
            ]
        )
    )

    context = ssl.create_default_context()

    if smtp_use_tls:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.starttls(context=context)
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(msg)
    else:
        with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15, context=context) as server:
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(msg)


def verify_admin_key(x_api_key: str | None) -> None:
    expected_key = os.getenv("ADMIN_API_KEY", "").strip()

    if not expected_key:
        raise HTTPException(status_code=503, detail="Admin API key is not configured")

    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "portfolio-api"}


@app.post("/api/contact", response_model=ContactMessageOut)
def create_contact_message(payload: ContactMessageIn) -> ContactMessageOut:
    created_at = datetime.now(timezone.utc).isoformat()

    try:
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO contact_messages (name, email, subject, message, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    payload.name.strip(),
                    payload.email,
                    payload.subject.strip(),
                    payload.message.strip(),
                    created_at,
                ),
            )
            conn.commit()
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail="Failed to store message") from exc

    try:
        send_email_notification(payload, created_at)
    except Exception:
        # Do not fail the main contact flow if email notification fails.
        pass

    return ContactMessageOut(ok=True, message="Message received. I will get back to you soon.")


@app.get("/api/messages", response_model=list[ContactMessageRecord])
def list_contact_messages(
    limit: int = Query(default=25, ge=1, le=100),
    x_api_key: str | None = Header(default=None, alias="x-api-key"),
) -> list[ContactMessageRecord]:
    verify_admin_key(x_api_key)

    try:
        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, name, email, subject, message, created_at
                FROM contact_messages
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail="Failed to read messages") from exc

    return [ContactMessageRecord(**dict(row)) for row in rows]
