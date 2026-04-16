from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Dict, Iterable

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

HEADER_FILL = PatternFill(fill_type="solid", fgColor="2D4A6B")
HEADER_FONT = Font(color="FFFFFF", bold=True)
MISSING_EMAIL_FILL = PatternFill(fill_type="solid", fgColor="FFE7E7")
MISSING_DEADLINE_FILL = PatternFill(fill_type="solid", fgColor="FFF5D6")

REQUIRED_OUTPUT_FIELDS = [
    "Full Name",
    "Student ID",
    "Email",
    "Assigned Sanctions",
]

OPTIONAL_OUTPUT_FIELDS = [
    "Next Deadline",
    "Next Deadline Reason",
    "Hold in Place",
    "File ID",
    "Hearing Date",
    "Assigned To / Hearing Officer",
]

HEADER_ALIASES = {
    "file_id": {"fileid", "file_id", "file id", "case id"},
    "full_name": {"full name", "student name", "name", "respondent name"},
    "first_name": {"first name", "firstname", "given name"},
    "last_name": {"last name", "lastname", "surname", "family name"},
    "student_id": {"student id", "sid", "id", "studentid"},
    "email": {"email", "email address", "student email"},
    "assigned_sanctions": {
        "assigned sanctions",
        "sanctions",
        "sanctions/actions",
        "sanctions actions",
        "actions",
        "assigned actions",
        "assigned sanction",
    },
    "next_deadline": {"next deadline", "deadline", "upcoming deadline"},
    "next_deadline_reason": {"next deadline reason", "deadline reason", "deadline notes"},
    "hold_in_place": {"hold in place", "hold", "conduct hold"},
    "hearing_date": {"hearing date", "resolution date", "meeting date"},
    "assigned_to": {"assigned to", "hearing officer", "assigned officer", "owner"},
}


class OverdueSanctionsError(Exception):
    pass


def _normalize_header(value: object) -> str:
    text = "" if value is None else str(value)
    lowered = " ".join(text.strip().lower().replace("_", " ").split())
    return "".join(ch for ch in lowered if ch.isalnum() or ch == " ").strip()


def _is_missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    return False


def _safe_cell_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    return str(value).strip()


def _find_column_indexes(ws: Worksheet) -> Dict[str, int]:
    first_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True), None)
    if not first_row:
        raise OverdueSanctionsError("The uploaded workbook is empty.")

    normalized_map = {}
    for idx, header in enumerate(first_row, start=1):
        key = _normalize_header(header)
        if key:
            normalized_map[key] = idx

    resolved: Dict[str, int] = {}
    for canonical, aliases in HEADER_ALIASES.items():
        for alias in aliases:
            alias_key = _normalize_header(alias)
            if alias_key in normalized_map:
                resolved[canonical] = normalized_map[alias_key]
                break

    if "assigned_sanctions" not in resolved:
        raise OverdueSanctionsError(
            "Missing sanctions/actions column. Please export the overdue sanctions report from Maxient and try again."
        )

    if "full_name" not in resolved and ("first_name" not in resolved or "last_name" not in resolved):
        raise OverdueSanctionsError(
            "Missing student name columns. Include Full Name or both First Name and Last Name in the export."
        )

    return resolved


def _build_output_row(row: tuple, columns: Dict[str, int]) -> Dict[str, str]:
    def pick(column_name: str) -> str:
        idx = columns.get(column_name)
        if not idx:
            return ""
        return _safe_cell_text(row[idx - 1])

    full_name = pick("full_name")
    if not full_name:
        full_name = " ".join(part for part in [pick("first_name"), pick("last_name")] if part).strip()

    return {
        "Full Name": full_name,
        "Student ID": pick("student_id"),
        "Email": pick("email"),
        "Assigned Sanctions": pick("assigned_sanctions"),
        "Next Deadline": pick("next_deadline"),
        "Next Deadline Reason": pick("next_deadline_reason"),
        "Hold in Place": pick("hold_in_place"),
        "File ID": pick("file_id"),
        "Hearing Date": pick("hearing_date"),
        "Assigned To / Hearing Officer": pick("assigned_to"),
    }


def _set_column_widths(ws: Worksheet, max_width: int = 52) -> None:
    for col_idx, column_cells in enumerate(ws.iter_cols(min_row=1, max_col=ws.max_column, max_row=ws.max_row), start=1):
        measured_width = 0
        for cell in column_cells:
            value = "" if cell.value is None else str(cell.value)
            longest_line = max((len(line) for line in value.splitlines()), default=0)
            measured_width = max(measured_width, longest_line)
        ws.column_dimensions[get_column_letter(col_idx)].width = min(max(12, measured_width + 2), max_width)


def _append_summary_sheet(workbook: Workbook, records: Iterable[Dict[str, str]]) -> None:
    records = list(records)
    summary = workbook.create_sheet(title="Summary")

    total_rows = len(records)
    missing_email = sum(1 for item in records if _is_missing(item.get("Email")))
    missing_deadline = sum(1 for item in records if _is_missing(item.get("Next Deadline")))
    hold_in_place = sum(
        1
        for item in records
        if item.get("Hold in Place", "").strip().lower() in {"yes", "y", "true", "1", "hold", "active"}
    )

    rows = [
        ("Metric", "Count"),
        ("Total rows", total_rows),
        ("Missing email", missing_email),
        ("Missing next deadline", missing_deadline),
        ("Hold in place (flagged)", hold_in_place),
    ]

    for row in rows:
        summary.append(row)

    for cell in summary[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT

    summary.column_dimensions["A"].width = 36
    summary.column_dimensions["B"].width = 14


def process_overdue_sanctions_workbook(content: bytes) -> bytes:
    try:
        source_wb = load_workbook(filename=BytesIO(content), data_only=True)
    except Exception as exc:
        raise OverdueSanctionsError("Invalid workbook. Please upload a valid .xlsx file exported from Maxient.") from exc

    source_ws = source_wb.active
    columns = _find_column_indexes(source_ws)

    output_wb = Workbook()
    detail_ws = output_wb.active
    detail_ws.title = "Overdue Sanctions"

    output_headers = REQUIRED_OUTPUT_FIELDS + OPTIONAL_OUTPUT_FIELDS
    detail_ws.append(output_headers)

    records = []
    for row in source_ws.iter_rows(min_row=2, values_only=True):
        mapped = _build_output_row(row, columns)
        if not any(value for value in mapped.values()):
            continue
        records.append(mapped)
        detail_ws.append([mapped[header] for header in output_headers])

    if not records:
        raise OverdueSanctionsError("No report rows were found in the uploaded workbook.")

    for cell in detail_ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="left", vertical="center")

    sanctions_col = output_headers.index("Assigned Sanctions") + 1
    email_col = output_headers.index("Email") + 1
    deadline_col = output_headers.index("Next Deadline") + 1

    for row_idx in range(2, detail_ws.max_row + 1):
        sanctions_cell = detail_ws.cell(row=row_idx, column=sanctions_col)
        sanctions_cell.alignment = Alignment(vertical="top", wrap_text=True)

        email_cell = detail_ws.cell(row=row_idx, column=email_col)
        if _is_missing(email_cell.value):
            email_cell.fill = MISSING_EMAIL_FILL

        deadline_cell = detail_ws.cell(row=row_idx, column=deadline_col)
        if _is_missing(deadline_cell.value):
            deadline_cell.fill = MISSING_DEADLINE_FILL

    detail_ws.freeze_panes = "A2"
    _set_column_widths(detail_ws)
    _append_summary_sheet(output_wb, records)

    stream = BytesIO()
    output_wb.save(stream)
    return stream.getvalue()
