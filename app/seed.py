from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import hash_password
from app.content_defaults import PAGES
from app.models import EditableContent, Role, User

INITIAL_USERS = [
    ("DAVE", "Stender@2026", "admin"),
    ("Stconduct", "Ga@2026", "user"),
]


def seed_roles_users_and_content(db: Session) -> None:
    roles = {}
    for role_name in ["admin", "user"]:
        role = db.scalar(select(Role).where(Role.name == role_name))
        if not role:
            role = Role(name=role_name)
            db.add(role)
            db.flush()
        roles[role_name] = role

    for username, password, role_name in INITIAL_USERS:
        existing = db.scalar(select(User).where(User.username == username))
        if not existing:
            db.add(User(username=username, password_hash=hash_password(password), role_id=roles[role_name].id))

    for page_name, page_data in PAGES.items():
        for section in page_data["sections"]:
            found = db.scalar(
                select(EditableContent).where(
                    EditableContent.page_name == page_name,
                    EditableContent.section_key == section["section_key"],
                )
            )
            if not found:
                db.add(
                    EditableContent(
                        page_name=page_name,
                        section_key=section["section_key"],
                        title=section["title"],
                        body=section["body"],
                        metadata_json=section.get("metadata_json"),
                    )
                )
    db.commit()
