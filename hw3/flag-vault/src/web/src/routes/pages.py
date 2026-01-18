"""Page routes for the web application."""

import sqlite3
import uuid
from functools import wraps
from typing import Annotated

from fastapi import APIRouter
from fastapi import Request
from fastapi import Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext

from utils import get_db_conn
from utils import flash
from utils import get_flashed_message

pages = APIRouter()
templates = Jinja2Templates(directory="templates")
templates.env.globals["get_flashed_message"] = get_flashed_message
passwd_context = CryptContext(schemes=["argon2"])


def login_required(func):
    """Decorator to require user login for page routes."""

    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        user = request.session.get("user")
        if not user:
            flash(request, "Please login to access this page", "error")
            return RedirectResponse(url="/login", status_code=303)
        return await func(request, *args, **kwargs)

    return wrapper


@pages.get("/")
async def index(request: Request):
    """Home page."""
    user = request.session.get("user")
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user,
        },
    )


@pages.get("/register")
async def register_get(request: Request):
    """Registration page."""
    # TODO: reCAPTCHA
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
        },
    )


@pages.post("/register")
async def register(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    """Handle user registration."""
    # Check password
    if len(password) < 8 or len(password) > 210:
        flash(request, "Invalid password", "error")
        return RedirectResponse(url="/register", status_code=303)

    # Check username
    if len(username) < 6 or len(username) > 210:
        flash(request, "Invalid username", "error")
        return RedirectResponse(url="/register", status_code=303)

    password_hash = passwd_context.hash(password)
    conn = get_db_conn()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)",
            (uuid.uuid4().hex, username, password_hash),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        flash(request, "Username already exists", "error")
        return RedirectResponse(url="/register", status_code=303)
    finally:
        conn.close()
    flash(request, "Registration successful! Please login", "success")
    return RedirectResponse(url="/login", status_code=303)


@pages.get("/login")
async def login_get(request: Request):
    """Login page."""
    # TODO: reCAPTCHA
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
        },
    )


@pages.post("/login")
async def login_post(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    """Handle user login."""
    conn = get_db_conn()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,),
    )
    user = c.fetchone()
    conn.close()
    if user and passwd_context.verify(password, user["password_hash"]):
        request.session["user"] = {"id": user["id"], "username": user["username"]}
        flash(request, f"Welcome back, {user['username']}!", "success")
        return RedirectResponse(url="/", status_code=303)
    else:
        flash(request, "Invalid username or password", "error")
        return RedirectResponse(url="/login", status_code=303)


@pages.post("/logout")
async def logout(request: Request):
    """Handle user logout."""
    request.session.pop("user", None)
    return RedirectResponse(url="/", status_code=303)


@pages.get("/flag")
@login_required
async def flag_page(request: Request):
    """Flag page."""
    user = request.session["user"]

    conn = get_db_conn()
    c = conn.cursor()
    c.execute(
        "SELECT id, content FROM flags WHERE owner_id = ?",
        (user["id"],),
    )
    flag = c.fetchone()
    conn.close()

    return templates.TemplateResponse(
        "flag.html",
        {
            "request": request,
            "flag": flag and flag["content"],
        },
    )


@pages.get("/admin")
@login_required
async def admin_page(request: Request):
    # TODO: Implement admin check to set session["is_admin"] to True
    if request.session.get("is_admin"):
        try:
            with open("/flag1.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            return "flag{test1}"
    flash(request, "You are not authorized to access this page", "error")
    return RedirectResponse(url="/", status_code=303)
