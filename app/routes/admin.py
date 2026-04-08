import json

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import enforce_csrf, get_csrf_token
from app.content_defaults import PAGES
from app.content_service import get_page_content
from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models import EditableContent, User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("")
def admin_home(request: Request, user: User = Depends(require_role("admin"))):
    templates = request.app.state.templates
    return templates.TemplateResponse(
        "admin_index.html",
        {"request": request, "user": user, "all_pages": PAGES, "csrf_token": get_csrf_token(request)},
    )


@router.get("/content/{page_name}")
def admin_edit_page(
    request: Request,
    page_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    if page_name not in PAGES:
        raise HTTPException(status_code=404)
    templates = request.app.state.templates
    return templates.TemplateResponse(
        "admin_page_edit.html",
        {
            "request": request,
            "user": user,
            "page_name": page_name,
            "page_label": PAGES[page_name]["label"],
            "sections": get_page_content(db, page_name),
            "all_pages": PAGES,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/content/{page_name}/{section_key}")
def admin_update_section(
    request: Request,
    page_name: str,
    section_key: str,
    title: str = Form(..., min_length=1, max_length=255),
    body: str = Form(..., min_length=1, max_length=10000),
    metadata_json: str = Form(""),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    enforce_csrf(request, csrf_token)
    content = db.scalar(
        select(EditableContent).where(
            EditableContent.page_name == page_name,
            EditableContent.section_key == section_key,
        )
    )
    if not content:
        raise HTTPException(status_code=404)

    parsed_metadata = None
    if metadata_json.strip():
        try:
            parsed_metadata = json.loads(metadata_json)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="metadata_json must be valid JSON") from exc

    content.title = title.strip()
    content.body = body.strip()
    content.metadata_json = parsed_metadata
    db.add(content)
    db.commit()

    return RedirectResponse(url=f"/admin/content/{page_name}", status_code=303)
