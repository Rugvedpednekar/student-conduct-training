from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

from app.auth import get_csrf_token
from app.content_defaults import PAGES
from app.content_service import get_page_content
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import ChatRequest
from app.services.nova_chat import NovaChatService
from app.services.overdue_sanctions import OverdueSanctionsError, process_overdue_sanctions_workbook

router = APIRouter()


def render_dynamic_page(request: Request, page_name: str, db: Session, user: User):
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


def render_static_template(request: Request, user: User, template_name: str, page_name: str):
    templates = request.app.state.templates

    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "user": user,
            "page_name": page_name,
            "page_label": PAGES[page_name]["label"] if page_name in PAGES else page_name.replace("-", " ").title(),
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
def dashboard(
    request: Request,
    user: User = Depends(get_current_user),
):
    return render_static_template(request, user, "index.html", "dashboard")


@router.get("/training-flow", response_class=HTMLResponse)
def training_flow(
    request: Request,
    user: User = Depends(get_current_user),
):
    return render_static_template(request, user, "training-flow.html", "training-flow")


@router.get("/office-overview", response_class=HTMLResponse)
def office_overview(
    request: Request,
    user: User = Depends(get_current_user),
):
    return render_static_template(request, user, "office-overview.html", "office-overview")


@router.get("/systems", response_class=HTMLResponse)
def systems(
    request: Request,
    user: User = Depends(get_current_user),
):
    return render_static_template(request, user, "systems.html", "systems")


@router.get("/responsibilities", response_class=HTMLResponse)
def responsibilities(
    request: Request,
    user: User = Depends(get_current_user),
):
    return render_static_template(request, user, "responsibilities.html", "responsibilities")


@router.get("/case-handling", response_class=HTMLResponse)
def case_handling(
    request: Request,
    user: User = Depends(get_current_user),
):
    return render_static_template(request, user, "case-handling.html", "case-handling")


@router.get("/sanctions", response_class=HTMLResponse)
def sanctions(
    request: Request,
    user: User = Depends(get_current_user),
):
    return render_static_template(request, user, "sanctions.html", "sanctions")


@router.get("/overdue-sanctions", response_class=HTMLResponse)
def overdue_sanctions_page(
    request: Request,
    user: User = Depends(get_current_user),
):
    return render_static_template(request, user, "overdue-sanctions.html", "overdue-sanctions")


@router.post("/api/overdue-sanctions/process")
async def process_overdue_sanctions(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    filename = file.filename or "overdue-sanctions.xlsx"
    if not filename.lower().endswith(".xlsx"):
        return JSONResponse(status_code=400, content={"detail": "Please upload a .xlsx file exported from Maxient."})

    uploaded_bytes = await file.read()
    if not uploaded_bytes:
        return JSONResponse(status_code=400, content={"detail": "Uploaded file is empty."})

    try:
        cleaned_content = process_overdue_sanctions_workbook(uploaded_bytes)
    except OverdueSanctionsError as exc:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    base_name = filename.rsplit(".", 1)[0]
    out_name = f"{base_name}-cleaned.xlsx"
    headers = {"Content-Disposition": f'attachment; filename="{out_name}"'}
    return Response(
        content=cleaned_content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.get("/parent-letters", response_class=HTMLResponse)
def parent_letters(
    request: Request,
    user: User = Depends(get_current_user),
):
    return render_static_template(request, user, "parent-letters.html", "parent-letters")


@router.get("/hearing", response_class=HTMLResponse)
def hearing_page(
    request: Request,
    user: User = Depends(get_current_user),
):
    return render_static_template(request, user, "hearing.html", "hearing")


@router.get("/ai-chat", response_class=HTMLResponse)
def ai_chat_page(
    request: Request,
    user: User = Depends(get_current_user),
):
    return render_static_template(request, user, "ai-chat.html", "ai-chat")


@router.post("/api/ai-chat", response_class=JSONResponse)
def ai_chat(
    payload: ChatRequest,
    user: User = Depends(get_current_user),
):
    service = NovaChatService()
    try:
        answer, sources = service.ask(payload.message, [message.model_dump() for message in payload.history])
        return {"answer": answer, "sources": sources}
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"detail": "AI Chat encountered an unexpected error. Please contact Student Conduct staff if this continues."},
        )


# Keep this only for pages that are still driven by database content + page.html
for route_name in []:

    @router.get(f"/{route_name}", name=f"view_{route_name}")
    def _view_page(
        request: Request,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
        page_name: str = route_name,
    ):
        return render_dynamic_page(request, page_name, db, user)
