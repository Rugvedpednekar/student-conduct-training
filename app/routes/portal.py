from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.auth import get_csrf_token
from app.content_defaults import PAGES
from app.content_service import get_page_content
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User

router = APIRouter()


def render_page(request: Request, page_name: str, db: Session, user: User):
    if page_name not in PAGES:
        raise HTTPException(status_code=404)

    sections = get_page_content(db, page_name)
    templates = request.app.state.templates
    return templates.TemplateResponse(
        "page.html",
        {
            "request": request,
            "user": user,
            "page_name": page_name,
            "page_label": PAGES[page_name]["label"],
            "sections": sections,
            "all_pages": PAGES,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.get("/")
def root_redirect(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/dashboard", status_code=303)
    return RedirectResponse(url="/login", status_code=303)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/training-flow", response_class=HTMLResponse)
async def training_flow(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse("training-flow.html", {"request": request})


for route_name in [
    "office-overview",
    "systems",
    "responsibilities",
    "case-handling",
    "sanctions",
    "parent-letters",
    "templates",
    "escalation",
    "quick-reference",
]:

    @router.get(f"/{route_name}", name=f"view_{route_name}")
    def _view_page(
        request: Request,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
        page_name: str = route_name,
    ):
        return render_page(request, page_name, db, user)
