"""Utility functions for database and flash messages."""

import sqlite3
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import Request
from markupsafe import escape

DB_PATH = "/tmp/data.db"


@asynccontextmanager
async def init_db(app: FastAPI):
    """Initialize database tables on startup."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);
""")
    c.execute("""
CREATE TABLE IF NOT EXISTS flags (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    owner_id TEXT NOT NULL UNIQUE,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);
""")

    conn.commit()
    conn.close()

    yield


def get_db_conn() -> sqlite3.Connection:
    """Get a database connection with Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def flash(request: Request, message: str, flash_type: str = "info"):
    """Set a flash message in the session."""
    request.session["flash_message"] = message
    request.session["flash_type"] = flash_type


def get_flashed_message(request: Request) -> str:
    """Get and remove flash message from session. Returns message as HTML."""
    message = request.session.pop("flash_message", "")
    flash_type = request.session.pop("flash_type", "info")
    if not message:
        return ""
    msg = (
        f"<div class='flash-message flash-{escape(flash_type)}'>{escape(message)}</div>"
    )
    try:
        # Try to format the message with the `request` for convenience
        # TODO: Someone said it's unsafe? Investigate further
        msg = msg.format(request=request)
    except Exception:
        pass
    return msg
