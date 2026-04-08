from sqlalchemy import select
from sqlalchemy.orm import Session

from app.content_defaults import PAGES
from app.models import EditableContent


def get_page_definition(page_name: str):
    return PAGES.get(page_name)


def get_page_content(db: Session, page_name: str) -> list[EditableContent]:
    rows = db.scalars(select(EditableContent).where(EditableContent.page_name == page_name).order_by(EditableContent.id)).all()
    if rows:
        return rows

    default = PAGES.get(page_name, {"sections": []})
    fallback = []
    for section in default["sections"]:
        fallback.append(
            EditableContent(
                page_name=page_name,
                section_key=section["section_key"],
                title=section["title"],
                body=section["body"],
                metadata_json=section.get("metadata_json"),
            )
        )
    return fallback
