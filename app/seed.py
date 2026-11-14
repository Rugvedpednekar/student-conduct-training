from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import hash_password
from app.config import settings
from app.content_defaults import PAGES
from app.models import EditableContent, Role, User


def _initial_accounts():
    accounts = (
        (settings.initial_admin_username, settings.initial_admin_password, "admin"),
        (settings.initial_user_username, settings.initial_user_password, "user"),
    )
    seen = set()
    for username, password, role in accounts:
        if bool(username) != bool(password):
            raise RuntimeError(f"Both username and password must be configured for initial {role} account")
        if not username:
            continue
        username = username.strip()
        if not username or len(username) > 60 or len(password) < 12:
            raise RuntimeError(f"Invalid initial {role} account: username max 60 chars, password min 12 chars")
        if username.casefold() in seen:
            raise RuntimeError("Bootstrap usernames must be unique")
        seen.add(username.casefold())
        yield username, password, role


def seed_roles_users_and_content(db: Session) -> None:
    accounts = list(_initial_accounts())
    roles = {}
    for role_name in ["admin", "user"]:
        role = db.scalar(select(Role).where(Role.name == role_name))
        if not role:
            role = Role(name=role_name)
            db.add(role)
            db.flush()
        roles[role_name] = role

    for username, password, role_name in accounts:
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
