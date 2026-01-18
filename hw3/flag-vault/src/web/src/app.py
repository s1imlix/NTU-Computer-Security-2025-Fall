"""Main FastAPI application."""

import os
from typing import Callable
from typing import Awaitable

from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from utils import init_db
from routes import api
from routes import pages


app = FastAPI(lifespan=init_db)
app.add_middleware(SessionMiddleware, secret_key=os.urandom(32).hex()) # Sign the session cookie with a random key
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register routes
app.include_router(api.api_flags)
app.include_router(pages.pages)


@app.middleware("http")
async def add_csp_header(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
):
    """Add Content-Security-Policy header to responses."""
    # Note: https://www.google.com/recaptcha/ is for the reCAPTCHA in the future
    # TODO: Maybe remove 'unsafe-eval' later
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; base-uri 'none'; "
        "script-src 'self' 'unsafe-eval' https://www.google.com/recaptcha/; "
        "style-src 'self' 'unsafe-inline'"
    )
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=11202)
