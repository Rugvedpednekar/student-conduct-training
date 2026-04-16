import os
import tempfile
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
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
_DOWNLOAD_TTL = timedelta(hours=1)
_generated_downloads: dict[str, dict[str, str | datetime]] = {}


def _cleanup_expired_downloads() -> None:
    now = datetime.utcnow()
    expired_ids = [
        file_id
        for file_id, metadata in _generated_downloads.items()
        if isinstance(metadata.get("expires_at"), datetime) and metadata["expires_at"] < now
    ]
    for file_id in expired_ids:
        metadata = _generated_downloads.pop(file_id, None)
        path = metadata.get("path") if metadata else None
        if isinstance(path, str) and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass


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
    date_from: str = Form(...),
    date_to: str = Form(...),
    user: User = Depends(get_current_user),
):
    filename = file.filename or "overdue-sanctions.xlsx"
    if not filename.lower().endswith(".xlsx"):
        return JSONResponse(status_code=400, content={"detail": "Please upload a .xlsx file exported from Maxient."})

    uploaded_bytes = await file.read()
    if not uploaded_bytes:
        return JSONResponse(status_code=400, content={"detail": "Uploaded file is empty."})

    try:
        parsed_date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        parsed_date_to = datetime.strptime(date_to, "%Y-%m-%d").date()
    except ValueError:
        return JSONResponse(status_code=400, content={"detail": "Invalid date format. Use YYYY-MM-DD."})

    if parsed_date_from > parsed_date_to:
        return JSONResponse(status_code=400, content={"detail": "Invalid date range. 'From' date cannot be later than 'To' date."})

    try:
        processed = process_overdue_sanctions_workbook(
            uploaded_bytes,
            date_from=parsed_date_from,
            date_to=parsed_date_to,
        )
    except OverdueSanctionsError as exc:
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    except Exception:
        return JSONResponse(status_code=400, content={"detail": "Spreadsheet parsing error. Please verify the uploaded export format."})

    base_name = filename.rsplit(".", 1)[0]
    out_name = f"{base_name}-cleaned.xlsx"
    temp_dir = tempfile.gettempdir()
    file_id = uuid.uuid4().hex
    temp_path = os.path.join(temp_dir, f"overdue-sanctions-{file_id}.xlsx")
    with open(temp_path, "wb") as output_file:
        output_file.write(processed.workbook_content)

    _cleanup_expired_downloads()
    _generated_downloads[file_id] = {
        "path": temp_path,
        "filename": out_name,
        "expires_at": datetime.utcnow() + _DOWNLOAD_TTL,
    }

    return JSONResponse(
        status_code=200,
        content={
            "total_rows": processed.total_rows,
            "preview_columns": processed.preview_columns,
            "preview_rows": processed.preview_rows,
            "download_url": f"/api/overdue-sanctions/download/{file_id}",
            "download_filename": out_name,
        },
    )


@router.get("/api/overdue-sanctions/download/{file_id}")
def download_overdue_sanctions_file(
    file_id: str,
    user: User = Depends(get_current_user),
):
    _cleanup_expired_downloads()
    file_info = _generated_downloads.get(file_id)
    if not file_info:
        return JSONResponse(status_code=404, content={"detail": "Download file not found or expired. Please process the report again."})

    path = file_info.get("path")
    filename = file_info.get("filename", "overdue-sanctions-cleaned.xlsx")
    if not isinstance(path, str) or not os.path.exists(path):
        _generated_downloads.pop(file_id, None)
        return JSONResponse(status_code=404, content={"detail": "Download file not found or expired. Please process the report again."})

    with open(path, "rb") as file_stream:
        content = file_stream.read()

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(
        content=content,
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
