"""API routes for flags."""

import uuid
from functools import wraps
from typing import Annotated

from fastapi import APIRouter
from fastapi import Request
from fastapi import Form
from fastapi import HTTPException

from utils import get_db_conn

api_flags = APIRouter(prefix="/api/flag", tags=["Flag API"])


def login_required(func):
    """Decorator to require user login for API routes."""

    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        user = request.session.get("user")
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return await func(request, *args, **kwargs)

    return wrapper


@api_flags.post("/")
@login_required
async def create_or_update_flag(
    request: Request,
    content: Annotated[str, Form()],
):
    """Create or update the flag for the current user."""
    user = request.session["user"]

    conn = get_db_conn()
    c = conn.cursor()

    # Check if user already has a flag
    c.execute(
        "SELECT id FROM flags WHERE owner_id = ?",
        (user["id"],),
    )
    existing = c.fetchone()

    if existing:
        # Update existing flag
        c.execute(
            "UPDATE flags SET content = ? WHERE owner_id = ?",
            (content, user["id"]),
        )
        flag_id = existing["id"]
    else:
        # Create new flag
        flag_id = uuid.uuid4().hex
        c.execute(
            "INSERT INTO flags (id, content, owner_id) VALUES (?, ?, ?)",
            (flag_id, content, user["id"]),
        )

    conn.commit()
    conn.close()

    return {"id": flag_id}
