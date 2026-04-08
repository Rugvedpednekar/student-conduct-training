from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import clear_user_session, enforce_csrf, get_csrf_token, set_user_session, verify_password
from app.database import get_db
from app.models import User

router = APIRouter()

def get_templates(request: Request) -> Jinja2Templates:
    return request.app.state.templates


@router.get("/login")
def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/dashboard", status_code=303)
    templates = get_templates(request)
    return templates.TemplateResponse("login.html", {"request": request, "csrf_token": get_csrf_token(request), "error": None})


@router.post("/login")
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    enforce_csrf(request, csrf_token)
    user = db.scalar(select(User).where(User.username == username))
    if not user or not verify_password(password, user.password_hash):
        templates = get_templates(request)
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "csrf_token": get_csrf_token(request), "error": "Invalid username or password."},
            status_code=400,
        )

    set_user_session(request, user.id, user.role.name, user.username)
    return RedirectResponse(url="/dashboard", status_code=303)


@router.post("/logout")
def logout(request: Request, csrf_token: str = Form(...)):
    enforce_csrf(request, csrf_token)
    clear_user_session(request)
    return RedirectResponse(url="/login", status_code=303)
