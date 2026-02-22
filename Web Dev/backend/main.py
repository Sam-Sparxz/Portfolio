from __future__ import annotations

import os
import smtplib
import ssl
import time
import threading
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine, desc
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Rate limiter using slowapi (Redis if configured, memory otherwise)
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.extension import _rate_limit_exceeded_handler

REDIS_URL = os.getenv("REDIS_URL", "")
storage_uri = REDIS_URL if REDIS_URL else "memory://"
limiter = Limiter(key_func=get_remote_address, storage_uri=storage_uri)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "portfolio.db"

DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{DB_PATH}"

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class ContactMessageModel(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(320), nullable=False)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(String(64), nullable=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


class ContactMessageIn(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    subject: str = Field(min_length=3, max_length=120)
    message: str = Field(min_length=10, max_length=2500)
    honeypot: Optional[str] = Field(default=None, max_length=200)


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


app = FastAPI(title="Portfolio API", version="1.2.0")

allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [item.strip() for item in allowed_origins_raw.split(",") if item.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# attach rate-limiter middleware and handler
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


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


def verify_admin_key(x_api_key: Optional[str]) -> None:
    expected_key = os.getenv("ADMIN_API_KEY", "").strip()

    if not expected_key:
        raise HTTPException(status_code=503, detail="Admin API key is not configured")

    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Unauthorized")


# NOTE: older in-memory limiter removed in favor of slowapi. Configure REDIS_URL
# in production for distributed rate limits.


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "portfolio-api"}


@limiter.limit("6/minute")
@app.post("/api/contact", response_model=ContactMessageOut)
def create_contact_message(payload: ContactMessageIn, request: Request) -> ContactMessageOut:
    # Honeypot check: if filled, treat as spam (silently drop)
    if payload.honeypot and payload.honeypot.strip():
        return ContactMessageOut(ok=True, message="Message received. I will get back to you soon.")

    created_at = datetime.now(timezone.utc).isoformat()

    try:
        session = SessionLocal()
        record = ContactMessageModel(
            name=payload.name.strip(),
            email=str(payload.email),
            subject=payload.subject.strip(),
            message=payload.message.strip(),
            created_at=created_at,
        )
        session.add(record)
        session.commit()
        session.refresh(record)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to store message") from exc
    finally:
        try:
            session.close()
        except Exception:
            pass

    try:
        send_email_notification(payload, created_at)
    except Exception:
        # Do not fail the main contact flow if email notification fails.
        pass

    return ContactMessageOut(ok=True, message="Message received. I will get back to you soon.")


@app.get("/api/messages", response_model=list[ContactMessageRecord])
def list_contact_messages(
    limit: int = Query(default=25, ge=1, le=100),
    x_api_key: Optional[str] = Header(default=None, alias="x-api-key"),
) -> list[ContactMessageRecord]:
    verify_admin_key(x_api_key)

    try:
        session = SessionLocal()
        rows = (
            session.query(ContactMessageModel)
            .order_by(desc(ContactMessageModel.id))
            .limit(limit)
            .all()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to read messages") from exc
    finally:
        try:
            session.close()
        except Exception:
            pass

    return [
        ContactMessageRecord(
            id=r.id,
            name=r.name,
            email=r.email,
            subject=r.subject,
            message=r.message,
            created_at=r.created_at,
        )
        for r in rows
    ]
