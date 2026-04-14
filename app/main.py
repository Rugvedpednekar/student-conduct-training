from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routes import admin, auth, portal
from app.seed import seed_roles_users_and_content


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_roles_users_and_content(db)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie=settings.session_cookie_name,
    same_site="lax",
    https_only=settings.secure_cookies,
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
app.state.templates = templates

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(portal.router)


@app.exception_handler(HTTPException)
async def auth_redirect_handler(request: Request, exc: HTTPException):
    if exc.status_code in {401, 403} and request.url.path.startswith("/admin"):
        return RedirectResponse(url="/dashboard", status_code=303)
    if exc.status_code == 401:
        return RedirectResponse(url="/login", status_code=303)
    raise exc
