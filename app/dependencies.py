from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user


def require_role(role_name: str):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role.name.lower() != role_name.lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return user

    return checker
